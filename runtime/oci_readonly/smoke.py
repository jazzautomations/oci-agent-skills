"""MCP stdio smoke with asynchronous reads and real deadlines; prints no inventory."""

import argparse
import asyncio
import configparser
from pathlib import Path
import json
import os
import sys
from datetime import datetime, timedelta, timezone

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from oracle_mcp_common import AuthOptions, build_auth_context

EXPECTED = {
    "oci_regions",
    "oci_compartments",
    "oci_instances",
    "oci_network_inventory",
    "oci_buckets",
    "oci_resource_search",
    "oci_limit_services",
    "oci_limit_values",
    "oci_whoami",
    "oci_work_requests",
    "oci_alarm_status",
    "oci_audit_events",
    "oci_metrics",
    "oci_price_lookup",
    "oci_cost_summary",
}


async def run(live: bool, region: str, timeout: float) -> dict:
    parameters = StdioServerParameters(
        command=sys.executable, args=["-m", "oci_readonly.server"], env=dict(os.environ)
    )
    report = {"transport": "stdio", "live": live, "checks": []}
    async with asyncio.timeout(timeout):
        async with stdio_client(parameters) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                discovered = (await session.list_tools()).tools
                assert {t.name for t in discovered} == EXPECTED, "Unexpected tool surface"
                assert all(
                    t.annotations
                    and t.annotations.readOnlyHint
                    and not t.annotations.destructiveHint
                    for t in discovered
                ), "Missing read-only annotations"
                report["tool_count"] = len(discovered)
                schema = json.dumps(
                    [t.model_dump(exclude_none=True) for t in discovered], separators=(",", ":")
                )
                report["schema_characters"] = len(schema)
                report["schema_tokens_estimate"] = (len(schema) + 3) // 4
                assert report["schema_tokens_estimate"] <= 3500, "Schema estimate exceeds the foundation budget"
                # Invalid input must be rejected without any OCI credential access.
                invalid = await session.call_tool(
                    "oci_instances", {"compartment_id": "invalid", "region": region}
                )
                assert invalid.isError, "Schema validation did not reject invalid scope"
                report["checks"].append({"name": "invalid_scope_rejected", "ok": True})
                if live:
                    context = await asyncio.to_thread(
                        build_auth_context, AuthOptions(region=region)
                    )
                    tenancy = context.tenancy_id
                    if not tenancy:
                        raise RuntimeError("Authentication did not resolve tenancy")
                    compartment = os.getenv("OCI_SMOKE_COMPARTMENT_ID", tenancy)
                    base = {"compartment_id": compartment, "region": region, "page_size": 1}
                    tenant_base = {"tenancy_id": tenancy, "region": region, "page_size": 1}
                    end = datetime.now(timezone.utc).date()
                    calls = [
                        ("oci_whoami", {}),
                        ("oci_price_lookup", {"part_number": "B88514", "currency": "USD"}),
                        ("oci_regions", {**tenant_base, "page_size": 100}),
                        ("oci_compartments", base),
                        ("oci_network_inventory", base),
                        ("oci_network_inventory", {**base, "resource": "subnets"}),
                        ("oci_buckets", base),
                        ("oci_resource_search", base),
                        ("oci_limit_services", tenant_base),
                        ("oci_limit_values", {**tenant_base, "service_name": "compute"}),
                        (
                            "oci_cost_summary",
                            {
                                **base,
                                "start_date": str(end - timedelta(days=1)),
                                "end_date": str(end),
                            },
                        ),
                    ]
                    report["shape_only_tools"] = sorted(EXPECTED - {name for name, _ in calls})
                    report["live_scope"] = "D7 only; skipped tools have offline/schema coverage"
                    report["shape_only_reasons"] = {name:("Tool summarizes metric datapoints; it does not expose D7 metric-metadata list." if name == "oci_metrics" else "No approved deployed-resource fixture in this smoke.") for name in report["shape_only_tools"]}
                    for name, arguments in calls:
                        response = await session.call_tool(name, arguments)
                        payload = response.structuredContent
                        if payload is None:
                            payload = json.loads(response.content[0].text)
                        check = {
                            "name": name,
                            "variant": arguments.get("resource"),
                            "ok": bool(payload.get("ok")) and not response.isError,
                        }
                        if check["ok"]:
                            check.update(count=payload["count"], truncated=payload["truncated"])
                            if name == "oci_price_lookup" and not payload["count"]:
                                check.update(ok=False, error_kind="public_sku_not_found")
                        else:
                            # Error dictionaries are server-sanitized; no raw MCP text or IDs.
                            check["error_kind"] = payload.get("error", {}).get(
                                "kind", "protocol_error"
                            )
                            check["status"] = payload.get("error", {}).get("status")
                        report["checks"].append(check)
    report["ok"] = all(check["ok"] for check in report["checks"])
    return report


def profile_region():
    """Read only the selected profile's region; no signer or credential validation."""
    config = configparser.ConfigParser(interpolation=None)
    location = os.getenv('OCI_CONFIG_FILE') or os.getenv('OCI_CLI_CONFIG_FILE') or '~/.oci/config'
    profile = os.getenv('OCI_CONFIG_PROFILE') or os.getenv('OCI_CLI_PROFILE') or 'DEFAULT'
    try:
        config.read(Path(location).expanduser())
        return config.get(profile, 'region', fallback=None)
    except (OSError, configparser.Error):
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live",
        action="store_true",
        help="Make allowlisted OCI read calls using local credentials.",
    )
    parser.add_argument("--region", default=os.getenv("OCI_REGION"))
    parser.add_argument("--timeout", type=float, default=180)
    options = parser.parse_args()
    if options.live and not options.region:
        options.region = profile_region()
        if not options.region:
            parser.error("Set --region, OCI_REGION, or a region in the selected profile")
    try:
        # Offline smoke uses a syntactically valid region only; it makes no OCI calls.
        report = asyncio.run(run(options.live, options.region or "us-ashburn-1", options.timeout))
    except TimeoutError:
        report = {"ok": False, "error": "Smoke deadline exceeded; child process was closed."}
    except Exception:
        report = {
            "ok": False,
            "error": "Smoke failed; check local authentication, installation or protocol. Details suppressed.",
        }
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
