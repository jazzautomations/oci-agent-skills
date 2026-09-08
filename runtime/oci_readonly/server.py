"""Fixed OCI read operations. No SDK reflection, CLI, SQL, or mutation tool."""

import functools
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal

import oci
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from oracle_mcp_common import AuthOptions, build_auth_context
from pydantic import Field

from . import __version__

mcp = FastMCP("oci-readonly", log_level="WARNING")
READ = ToolAnnotations(
    readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=True
)
PageSize = Annotated[int, Field(ge=1, le=100, description="Maximum rows in this single page.")]
Cursor = Annotated[
    str | None,
    Field(
        max_length=8192,
        description="Opaque next_cursor from this operation with unchanged scope and filters.",
    ),
]
Region = Annotated[str, Field(pattern=r"^[a-z][a-z0-9]*(-[a-z0-9]+)+-[0-9]+$", max_length=80)]
Scope = Annotated[
    str,
    Field(
        pattern=r"^ocid1\.(compartment|tenancy)\.[a-z0-9]+\.[a-z0-9-]*\.[A-Za-z0-9_-]+$",
        max_length=255,
    ),
]
FIELDS = {
    "regions": ("region_name", "region_key", "status", "is_home_region"),
    "compartments": ("id", "name", "lifecycle_state", "compartment_id"),
    "instances": (
        "id",
        "display_name",
        "lifecycle_state",
        "shape",
        "availability_domain",
        "compartment_id",
        "time_created",
    ),
    "vcns": ("id", "display_name", "lifecycle_state", "compartment_id", "time_created"),
    "subnets": (
        "id",
        "display_name",
        "lifecycle_state",
        "vcn_id",
        "compartment_id",
        "prohibit_public_ip_on_vnic",
    ),
    "network_security_groups": (
        "id",
        "display_name",
        "vcn_id",
        "compartment_id",
        "lifecycle_state",
    ),
    "buckets": ("name", "compartment_id", "time_created"),
    "search": (
        "identifier",
        "resource_type",
        "display_name",
        "lifecycle_state",
        "compartment_id",
        "availability_domain",
        "time_created",
    ),
    "limit_services": ("name", "description"),
    "limit_values": ("name", "value", "scope_type", "availability_domain"),
    "costs": ("service", "currency", "computed_amount", "time_usage_started", "time_usage_ended"),
}


class ScopeError(ValueError):
    pass


class AuthenticationError(Exception):
    pass


def scope_id(value: str) -> str:
    if not re.fullmatch(
        r"ocid1\.(compartment|tenancy)\.[a-z0-9]+\.[a-z0-9-]*\.[A-Za-z0-9_-]+", value
    ):
        raise ScopeError("A valid compartment or tenancy OCID is required.")
    return value


@functools.lru_cache(maxsize=8)
def auth(region: str):
    if not re.fullmatch(r"[a-z][a-z0-9]*(-[a-z0-9]+)+-[0-9]+", region):
        raise ScopeError("Use an OCI region name, not a URL.")
    try:
        return build_auth_context(AuthOptions(region=region))
    except Exception:
        raise AuthenticationError() from None


def check_scope(compartment_id: str, region: str, *, tenancy_only: bool = False):
    scope_id(compartment_id)
    context = auth(region)
    if tenancy_only:
        if compartment_id != context.tenancy_id:
            raise ScopeError("Tenancy must match the authenticated tenancy.")
    else:
        configured = os.getenv("OCI_ALLOWED_COMPARTMENT_IDS", "")
        allowed = {scope_id(v.strip()) for v in configured.split(",") if v.strip()}
        if allowed and compartment_id not in allowed:
            raise ScopeError("Compartment is outside OCI_ALLOWED_COMPARTMENT_IDS.")
    return context


def client(factory, region: str):
    context = auth(region)
    config = {**context.config, "additional_user_agent": f"oci-readonly-mcp/{__version__}"}
    kwargs = {"timeout": (5, 25), "retry_strategy": oci.retry.NoneRetryStrategy()}
    if context.signer is not None:
        kwargs["signer"] = context.signer
    return factory(config, **kwargs)


def guarded(fn):
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ScopeError:
            return {
                "ok": False,
                "error": {
                    "kind": "invalid_scope",
                    "message": "Check the region, OCID and configured compartment allowlist.",
                },
            }
        except AuthenticationError:
            return {
                "ok": False,
                "error": {
                    "kind": "authentication",
                    "message": "Check OCI_CONFIG_FILE, OCI_CONFIG_PROFILE, OCI_MCP_AUTH_TYPE and local credential files.",
                },
            }
        except (ValueError, TypeError):
            return {
                "ok": False,
                "error": {
                    "kind": "invalid_input",
                    "message": "Check the input format and documented bounds.",
                },
            }
        except oci.exceptions.ServiceError as exc:
            status = exc.status if isinstance(exc.status, int) else None
            return {
                "ok": False,
                "error": {
                    "kind": "oci_service",
                    "status": status,
                    "retryable": status in (429, 500, 502, 503, 504),
                    "message": "OCI rejected the read. Check IAM, region, resource scope, and service availability.",
                },
            }
        except Exception:
            return {
                "ok": False,
                "error": {
                    "kind": "configuration_or_transport",
                    "message": "Check OCI authentication and connectivity locally; raw exception details are suppressed.",
                },
            }

    return wrapped


def shaped(rows, kind: str):
    # Intentionally excludes user data, tags, metadata, IPs, URLs and object contents.
    result = []
    for row in rows:
        data = row if isinstance(row, dict) else oci.util.to_dict(row)
        result.append({key: data[key] for key in FIELDS[kind] if key in data})
    return result


def page_result(response, kind: str, page_size: int, *, collection: bool = False):
    if not 1 <= page_size <= 100:
        raise ValueError("Invalid page size")
    rows = response.data.items if collection else response.data
    next_cursor = response.headers.get("opc-next-page") or None
    # OCI is expected to respect limit. Never silently skip oversized response rows.
    oversized = len(rows) > page_size
    return {
        "ok": True,
        "items": shaped(rows[:page_size], kind),
        "count": min(len(rows), page_size),
        "truncated": bool(next_cursor) or oversized,
        "next_cursor": None if oversized else next_cursor,
        "pagination_error": "OCI returned more rows than requested; continuation is unavailable."
        if oversized
        else None,
        "scope_note": "Only this region and explicit scope were queried. A page is not a complete inventory.",
    }


@mcp.tool(annotations=READ)
@guarded
def oci_regions(tenancy_id: Scope, region: Region, page_size: PageSize = 100) -> dict:
    """List the authenticated tenancy's region subscriptions; no cloud writes."""
    check_scope(tenancy_id, region, tenancy_only=True)
    response = client(oci.identity.IdentityClient, region).list_region_subscriptions(tenancy_id)
    return page_result(response, "regions", page_size)


@mcp.tool(annotations=READ)
@guarded
def oci_compartments(
    compartment_id: Scope, region: Region, page_size: PageSize = 50, cursor: Cursor = None
) -> dict:
    """Discover immediate child compartments; no recursive tenancy traversal. An allowlisted parent permits discovery of its child metadata, not reads inside those children."""
    check_scope(compartment_id, region)
    response = client(oci.identity.IdentityClient, region).list_compartments(
        compartment_id,
        access_level="ACCESSIBLE",
        compartment_id_in_subtree=False,
        limit=page_size,
        page=cursor,
    )
    return page_result(response, "compartments", page_size)


@mcp.tool(annotations=READ)
@guarded
def oci_instances(
    compartment_id: Scope, region: Region, page_size: PageSize = 50, cursor: Cursor = None
) -> dict:
    """Read one page of compute instance summaries; excludes metadata, tags, addresses and user data."""
    check_scope(compartment_id, region)
    response = client(oci.core.ComputeClient, region).list_instances(
        compartment_id, limit=page_size, page=cursor
    )
    return page_result(response, "instances", page_size)


@mcp.tool(annotations=READ)
@guarded
def oci_network_inventory(
    compartment_id: Scope,
    region: Region,
    resource: Literal["vcns", "subnets", "network_security_groups"] = "vcns",
    page_size: PageSize = 50,
    cursor: Cursor = None,
) -> dict:
    """Read one page of VCN, subnet or NSG summaries; does not fetch rules, routes or traffic."""
    check_scope(compartment_id, region)
    network = client(oci.core.VirtualNetworkClient, region)
    operations = {
        "vcns": network.list_vcns,
        "subnets": network.list_subnets,
        "network_security_groups": network.list_network_security_groups,
    }
    response = operations[resource](compartment_id=compartment_id, limit=page_size, page=cursor)
    return page_result(response, resource, page_size)


@mcp.tool(annotations=READ)
@guarded
def oci_buckets(
    compartment_id: Scope, region: Region, page_size: PageSize = 50, cursor: Cursor = None
) -> dict:
    """Read bucket metadata only; resolves namespace internally. Never lists or downloads objects."""
    check_scope(compartment_id, region)
    storage = client(oci.object_storage.ObjectStorageClient, region)
    namespace = storage.get_namespace().data
    response = storage.list_buckets(namespace, compartment_id, limit=page_size, page=cursor)
    return page_result(response, "buckets", page_size)


@mcp.tool(annotations=READ)
@guarded
def oci_resource_search(
    compartment_id: Scope, region: Region, page_size: PageSize = 50, cursor: Cursor = None
) -> dict:
    """Read resource-search summaries in exactly one compartment. No caller-supplied query language; search is eventually consistent and excludes unsupported types."""
    check_scope(compartment_id, region)
    details = oci.resource_search.models.StructuredSearchDetails(
        query=f"query all resources where compartmentId = '{compartment_id}'", type="Structured"
    )
    response = client(oci.resource_search.ResourceSearchClient, region).search_resources(
        details, limit=page_size, page=cursor
    )
    return page_result(response, "search", page_size, collection=True)


@mcp.tool(annotations=READ)
@guarded
def oci_limit_services(
    tenancy_id: Scope, region: Region, page_size: PageSize = 50, cursor: Cursor = None
) -> dict:
    """Discover service names for OCI limits in the authenticated tenancy. Tenancy metadata is separate from compartment restrictions."""
    check_scope(tenancy_id, region, tenancy_only=True)
    response = client(oci.limits.LimitsClient, region).list_services(
        tenancy_id, limit=page_size, page=cursor
    )
    return page_result(response, "limit_services", page_size)


@mcp.tool(annotations=READ)
@guarded
def oci_limit_values(
    tenancy_id: Scope,
    region: Region,
    service_name: Annotated[str, Field(pattern=r"^[a-z0-9-]+$", max_length=100)],
    page_size: PageSize = 50,
    cursor: Cursor = None,
) -> dict:
    """Read configured limit values for a service; these are NOT current usage or capacity guarantees."""
    check_scope(tenancy_id, region, tenancy_only=True)
    response = client(oci.limits.LimitsClient, region).list_limit_values(
        tenancy_id, service_name, limit=page_size, page=cursor
    )
    return page_result(response, "limit_values", page_size)


@mcp.tool(annotations=READ)
@guarded
def oci_cost_summary(
    compartment_id: Scope,
    region: Region,
    start_date: Annotated[str, Field(pattern=r"^\d{4}-\d{2}-\d{2}$")],
    end_date: Annotated[str, Field(pattern=r"^\d{4}-\d{2}-\d{2}$")],
    page_size: PageSize = 50,
    cursor: Cursor = None,
) -> dict:
    """Read reported costs grouped by service/currency for an exact compartment and region. UTC dates, end exclusive, max 31 days; excludes child compartments. No full-total claim when truncated; data can lag and is not a quote."""
    context = check_scope(compartment_id, region)
    start = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    end = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    if not timedelta(0) < end - start <= timedelta(days=31):
        raise ValueError("Cost window must be between 1 and 31 days")
    if not context.tenancy_id:
        raise ScopeError("Authentication must resolve the tenancy")
    models = oci.usage_api.models
    details = models.RequestSummarizedUsagesDetails(
        tenant_id=context.tenancy_id,
        time_usage_started=start,
        time_usage_ended=end,
        granularity="DAILY",
        query_type="COST",
        is_aggregate_by_time=True,
        group_by=["service", "currency"],
        filter=models.Filter(
            operator="AND",
            dimensions=[
                models.Dimension(key="compartmentId", value=compartment_id),
                models.Dimension(key="region", value=region),
            ],
        ),
    )
    response = client(oci.usage_api.UsageapiClient, region).request_summarized_usages(
        details, limit=page_size, page=cursor
    )
    result = page_result(response, "costs", page_size, collection=True)
    result["scope_note"] = (
        "Reported cost for this exact compartment and region only; excludes descendants. End date is exclusive; data may lag. No cross-currency total is computed."
    )
    return result


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
