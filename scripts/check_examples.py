#!/usr/bin/env python3
"""Validate published CLI examples offline; explicitly opt into bounded read-only live checks."""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from inventory import load_cli
from lib.oci_ro import run_process as run_readonly, ReadOnlyRefusal

# Exact read operations, individually reviewed. Never infer authorization from verbs.
LIVE_PATHS = {
    "iam compartment list", "iam region list", "iam region-subscription list",
    "iam availability-domain list", "iam policy list", "iam user list",
    "iam domain list", "iam dynamic-group list", "iam tag-namespace list",
    "iam tag-default list", "iam tag list-cost-tracking",
    "compute shape list", "compute image list", "network vcn list", "network subnet list",
    "os ns get", "os bucket list", "search resource structured-search",
    "limits service list", "limits value list", "limits definition list",
    "limits quota list", "limits resource-availability get",
    "usage-api usage-summary request-summarized-usages", "monitoring metric list",
}

PLACEHOLDERS = {'FILE_SYSTEM_ID', 'JOB_ID', 'PROBLEM_ID', 'ADB_ID', 'DOMAIN_URL', 'SECURITY_ZONE_ID', 'REGION', 'BUDGET_ID', 'USER_ID', 'STACK_ID', 'START_TIME', 'BACKEND_SET', 'CATALOG_ID', 'PREFIX', 'APPLICATION_ID', 'END_TIME', 'PROFILE', 'NETWORK_FIREWALL_POLICY_ID', 'SHAPE', 'TOPIC_ID', 'NSG_ID', 'PROJECT_ID', 'LOG_GROUP_ID', 'HOST_VULNERABILITY_ID', 'CLUSTER_ID', 'DR_GROUP_ID', 'TENANCY_ID', 'LIMIT_NAME', 'SESSION_ID', 'LOAD_BALANCER_ID', 'COMPARTMENT_ID', 'AD', 'BASTION_ID', 'INSTANCE_ID', 'METRIC_NAMESPACE', 'WORK_REQUEST_ID', 'POOL_ID', 'OBJECT_NAME', 'MGMT_ENDPOINT', 'ODA_ID', 'MQL', 'BUCKET', 'PRIVATE_ENDPOINT_ID', 'AVAILABILITY_DOMAIN', 'DEPLOY_PIPELINE_ID', 'POLICY_ID', 'NAMESPACE', 'CONNECTION_ID', 'BUILD_RUN_ID', 'REQUEST_ID', 'MANAGED_DB_ID', 'LB_ID'}
# Used by the shape-only default-route example; this adds no live authorization.
PLACEHOLDERS.add('VCN_ID')
# Live examples may use only these operational options. No CLI config, endpoint,
# filesystem, wait, query-output, raw body, debug, or all-pages options are accepted.
LIVE_FLAGS = {
    "--compartment-id",
    "--tenancy-id",
    "--tenant-id",
    "--limit",
    "--page-size",
    "--namespace-name",
    "--service-name",
    "--limit-name",
    "--availability-domain",
    "--query-text",
    "--time-usage-started",
    "--time-usage-ended",
    "--granularity",
    "--group-by",
    "--query-type",
    "--is-aggregate-by-time",
    "--compartment-depth",
    "--access-level",
    "--compartment-id-in-subtree",
    "--lifecycle-state",
    "--sort-by",
    "--sort-order",
    "--scope-type",
    "--vcn-id",
    "--name",
    "--operating-system",
}


def validate_example(example, root):
    import click

    argv = example.get("argv")
    if (
        not isinstance(argv, list)
        or not argv
        or not all(isinstance(arg, str) for arg in argv)
    ):
        raise ValueError("argv must be a nonempty string array")
    if not re.fullmatch(r"[a-zA-Z0-9_.-]{1,100}", example.get("id", "")):
        raise ValueError("invalid example ID")
    command, path, index = root, [], 0
    while isinstance(command, click.Group):
        if index >= len(argv) or argv[index] not in command.commands:
            raise ValueError("unknown or incomplete command path")
        path.append(argv[index])
        command = command.commands[argv[index]]
        index += 1
    options = {
        name: parameter
        for parameter in [*root.params, *command.params]
        if isinstance(parameter, click.Option)
        for name in parameter.opts + parameter.secondary_opts
    }
    supplied, values = set(), {}
    while index < len(argv):
        option = argv[index]
        if option not in options:
            raise ValueError("unknown option or unexpected positional argument")
        parameter = options[option]
        if parameter.name in supplied and not parameter.multiple:
            raise ValueError("duplicate option")
        supplied.add(parameter.name)
        nargs = 0 if parameter.is_flag else parameter.nargs
        if index + nargs >= len(argv):
            raise ValueError("missing option value")
        value = argv[index + 1] if nargs == 1 else None
        if nargs > 0 and argv[index + 1].startswith("--"):
            raise ValueError("missing option value")
        values[option] = value
        index += nargs + 1
    for parameter in command.params:
        required = (
            parameter.required
            or "[required]" in (getattr(parameter, "help", "") or "").lower()
        )
        if required and parameter.name not in supplied:
            raise ValueError("missing required option")
    for token in argv:
        if any(
            name not in PLACEHOLDERS for name in re.findall(r"\$\{([^}]+)\}", token)
        ):
            raise ValueError("unknown placeholder")
    # Generate installed command help without invoking command or credential callbacks.
    command.get_help(click.Context(command, info_name=" ".join(path)))
    return " ".join(path), values, options


def live_argv(example, path, values, available, substitutions):
    if path not in LIVE_PATHS or any(flag not in LIVE_FLAGS for flag in values):
        raise ValueError("command or option is not in the live allowlist")
    for flag, placeholder in {
        "--compartment-id": "${TENANCY_ID}"
        if path.startswith("limits ")
        else "${COMPARTMENT_ID}",
        "--tenancy-id": "${TENANCY_ID}",
        "--tenant-id": "${TENANCY_ID}",
    }.items():
        if flag in values and values[flag] not in ({placeholder, "${TENANCY_ID}"} if flag == "--compartment-id" else {placeholder}):
            raise ValueError("live scope must use the configured scope placeholder")
    if values.get("--compartment-id-in-subtree", "false").lower() != "false":
        raise ValueError("live checks cannot recursively traverse compartments")
    if path == "search resource structured-search":
        expected = "query all resources where compartmentId = '${COMPARTMENT_ID}'"
        if values.get("--query-text") != expected:
            raise ValueError("live search requires the fixed exact-compartment query")
    if path == "usage-api usage-summary request-summarized-usages":
        if (
            values.get("--time-usage-started") != "${START_TIME}"
            or values.get("--time-usage-ended") != "${END_TIME}"
        ):
            raise ValueError("live cost window must use bounded date placeholders")
        if (
            values.get("--granularity") != "DAILY"
            or values.get("--query-type", "COST") != "COST"
        ):
            raise ValueError("live costs require DAILY/COST")
        if json.loads(values.get("--group-by", '["service"]')) != ["service"]:
            raise ValueError("live costs only group by service")
    result = []
    for token in example["argv"]:
        for name in re.findall(r"\$\{([^}]+)\}", token):
            if name not in substitutions:
                raise ValueError("required placeholder is not configured")
            token = token.replace("${" + name + "}", substitutions[name])
        result.append(token)
    for flag in ("--limit", "--page-size"):
        if flag in values:
            result[result.index(flag) + 1] = "1"
    if "--limit" in available and "--limit" not in values:
        result += ["--limit", "1"]
    return result


def run_live(argv, profile, region):
    command = [
        sys.executable,
        "-m",
        "oci_cli.cli",
        "--profile",
        profile,
        "--region",
        region,
        "--output",
        "json",
        "--no-retry",
        "--connection-timeout",
        "5",
        "--read-timeout",
        "20",
        *argv,
    ]
    environment = dict(os.environ)
    environment["OCI_CLI_SUPPRESS_FILE_PERMISSIONS_WARNING"] = "True"
    # OCI checks presence, not truthiness: even "False" enables interactive mode.
    environment.pop("OCI_CLI_AUTO_PROMPT", None)
    try:
        completed = run_readonly(
            command[3:], executable=command[:3],
            capture_output=True,
            text=True,
            timeout=30,
            env=environment,
            stdin=subprocess.DEVNULL,
        )
    except ReadOnlyRefusal:
        return {"status": "failed", "error": "read_only_refusal"}
    except subprocess.TimeoutExpired:
        return {"status": "timeout"}
    if completed.returncode:
        # Never echo stderr, which may contain credentials, OCIDs, names or URLs.
        result = {"status": "failed", "exit_code": completed.returncode}
        try:
            error, _ = json.JSONDecoder().raw_decode(
                completed.stderr[completed.stderr.index("{") :]
            )
            if isinstance(error.get("status"), int):
                result["http_status"] = error["status"]
            code = error.get("code", "")
            if isinstance(code, str) and re.fullmatch(
                r"[A-Za-z][A-Za-z0-9]{0,80}", code
            ):
                result["error_code"] = code
        except (ValueError, TypeError, AttributeError):
            pass
        return result
    # OCI's render() deliberately prints nothing for an empty list with no
    # displayable headers. This is a successful empty read, not malformed JSON.
    if not completed.stdout.strip():
        return {
            "status": "passed",
            "count": 0,
            "truncated": False,
            "output_kind": "empty_cli_response",
        }
    try:
        payload = json.loads(completed.stdout)
    except (ValueError, TypeError):
        return {"status": "invalid_json"}
    data = payload.get("data")
    result = {"status": "passed"}
    if isinstance(data, list):
        result["count"] = len(data)
    elif isinstance(data, dict) and isinstance(data.get("items"), list):
        result["count"] = len(data["items"])
    result["truncated"] = bool(payload.get("opc-next-page"))
    return result


def discover_namespace(profile, region):
    """Return a private substitution and a public status; a failed read stays failed."""
    environment = dict(os.environ)
    environment.pop("OCI_CLI_AUTO_PROMPT", None)
    try:
        response = run_readonly(
            ["--profile", profile, "--region", region, "--output", "json",
             "--no-retry", "--connection-timeout", "5", "--read-timeout", "20",
             "os", "ns", "get"],
            capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL,
            env=environment,
        )
        if response.returncode:
            return None, {"status": "failed", "error": "namespace_discovery_failed",
                          "exit_code": response.returncode}
        value = json.loads(response.stdout)["data"]
        if not isinstance(value, str) or not value:
            raise ValueError("invalid namespace response")
        return value, {"status": "passed"}
    except (ValueError, KeyError, TypeError, subprocess.TimeoutExpired, ReadOnlyRefusal):
        return None, {"status": "failed", "error": "namespace_discovery_failed"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--examples",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "catalog" / "examples.json",
    )
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--profile")
    parser.add_argument("--region")
    parser.add_argument("--compartment-id")
    parser.add_argument(
        "--only", nargs="+", help="Validate only these catalog example IDs."
    )
    parser.add_argument(
        "--report", type=Path, help="Write a sanitized JSON validation summary."
    )
    options = parser.parse_args()
    if options.live and (not options.profile or not options.region):
        parser.error("--live requires explicit --profile and --region")
    if options.live and (os.getenv("OCI_CLI_ENDPOINT") or os.getenv("OCI_ENDPOINT")):
        parser.error("an endpoint override is configured; remove it before live checks")
    if options.live and not re.fullmatch(
        r"[a-z][a-z0-9]*(-[a-z0-9]+)+-[0-9]+", options.region
    ):
        parser.error("invalid region")
    try:
        examples = json.loads(options.examples.read_text(encoding="utf-8"))["examples"]
        if options.only:
            if set(options.only) - {example["id"] for example in examples}:
                raise ValueError("unknown selected example ID")
            examples = [
                example for example in examples if example["id"] in options.only
            ]
        root, import_errors = load_cli()
        if import_errors:
            print(
                json.dumps(
                    {
                        "status": "failed",
                        "error": "cli_import_errors",
                        "count": len(import_errors),
                    }
                )
            )
            return 1
        substitutions = {}
        bootstrap_checks = []
        if options.live:
            import oci

            config = oci.config.from_file(
                file_location=os.getenv(
                    "OCI_CLI_CONFIG_FILE", oci.config.DEFAULT_LOCATION
                ),
                profile_name=options.profile,
            )
            if config.get("endpoint"):
                raise ValueError("endpoint override in profile")
            tenancy = config["tenancy"]
            compartment = (
                options.compartment_id
                or os.getenv("OCI_SMOKE_COMPARTMENT_ID")
                or tenancy
            )
            for value in (tenancy, compartment):
                if not re.fullmatch(
                    r"ocid1\.(compartment|tenancy)\.[a-z0-9]+\.[a-z0-9-]*\.[A-Za-z0-9_-]+",
                    value,
                ):
                    raise ValueError("invalid configured scope")
            end = datetime.now(timezone.utc).date()
            substitutions = {
                "TENANCY_ID": tenancy,
                "COMPARTMENT_ID": compartment,
                "START_TIME": str(end - timedelta(days=1)) + "T00:00:00Z",
                "END_TIME": str(end) + "T00:00:00Z",
            }
            # Namespace discovery is a single scoped read; never retain its value.
            namespace, status = discover_namespace(options.profile, options.region)
            bootstrap_checks.append({"id": "namespace_discovery", **status})
            if namespace is not None:
                substitutions["NAMESPACE"] = namespace
            if os.getenv("OCI_SMOKE_NAMESPACE"):
                substitutions["NAMESPACE"] = os.environ["OCI_SMOKE_NAMESPACE"]
        failed = any(row["status"] != "passed" for row in bootstrap_checks)
        seen = set()
        reports = []
        for example in examples:
            identifier = example.get("id", "invalid")
            if not isinstance(identifier, str) or not re.fullmatch(
                r"[a-zA-Z0-9_.-]{1,100}", identifier
            ):
                identifier = "invalid"
            report = {"id": identifier}
            try:
                if identifier in seen:
                    raise ValueError("duplicate example ID")
                seen.add(identifier)
                path, values, available = validate_example(example, root)
                if options.live and example.get("live", True) and path in LIVE_PATHS:
                    try:
                        argv = live_argv(example, path, values, available, substitutions)
                    except ValueError:
                        report.update(status="shape-verified", reason="outside_bounded_live_template")
                        reports.append(report)
                        print(json.dumps(report))
                        continue
                    report.update(run_live(argv, options.profile, options.region))
                    if path == "usage-api usage-summary request-summarized-usages":
                        report["scope"] = (
                            "Tenancy-wide cost across compartments and resource regions; endpoint region is not a cost filter. UTC one-day window, one page."
                        )
                else:
                    report["status"] = "shape-verified" if options.live else "help_validated"
                    if options.live:
                        report["reason"] = "not_selected_for_D7_live"
            except (ValueError, KeyError, TypeError):
                report.update(status="failed", error="invalid_example_or_live_scope")
            failed |= report["status"] not in ("passed", "help_validated", "shape-verified")
            print(json.dumps(report))
            reports.append(report)
        if options.report:
            import importlib.metadata

            summary = {
                "mode": "live_read_only" if options.live else "offline_help",
                "validated_at": datetime.now(timezone.utc).isoformat(),
                "cli_version": importlib.metadata.version("oci-cli"),
                "sdk_version": importlib.metadata.version("oci"),
                "region": options.region if options.live else None,
                "complete": not failed,
                "scope_note": "Fixed read commands only. One page per call; no resource names, OCIDs, raw errors or credentials retained. Success validates a read API, not deployments or full inventory.",
                "checks": reports,
                "bootstrap_checks": bootstrap_checks,
            }
            options.report.parent.mkdir(parents=True, exist_ok=True)
            options.report.write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )
        return int(failed)
    except Exception:
        print(
            json.dumps({"status": "failed", "error": "local_configuration_or_catalog"})
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
