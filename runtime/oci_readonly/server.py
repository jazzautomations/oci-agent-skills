"""Fixed OCI read operations. No SDK reflection, CLI, SQL, or mutation tool."""

import functools
import json
import sys
import os
import re
import time
import threading
from pathlib import Path

import anyio
from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal

import oci
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from oracle_mcp_common import AuthOptions, build_auth_context
from pydantic import Field

from . import __version__

try:
    from .sanitize import envelope, emit
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
    from lib.sanitize import envelope, emit

class ProvenanceMCP(FastMCP):
    async def call_tool(self, name, arguments):
        from mcp.types import TextContent
        result = await super().call_tool(name, arguments)
        if isinstance(result, tuple) and len(result) == 2:
            content, structured = result
            if isinstance(structured, dict):
                return [TextContent(type='text', text=emit(structured))], structured
        if isinstance(result, list):
            for block in result:
                if isinstance(block, TextContent):
                    block.text = emit(json.loads(block.text))
        return result


mcp = ProvenanceMCP("oci-readonly", log_level="WARNING")
READ = ToolAnnotations(
    readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=True
)
PageSize = Annotated[int, Field(ge=1, le=100)]
Cursor = Annotated[
    str | None,
    Field(
        max_length=8192,
        description="Page cursor.",
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
    "costs": (
        "service",
        "currency",
        "compartment_id",
        "computed_amount",
        "time_usage_started",
        "time_usage_ended",
    ),
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


AUTH_TTL = 300
_AUTH_CACHE = {}
_AUTH_LOCK = threading.RLock()
_SCOPE_CACHE = {}


def file_stamp(path):
    try:
        stat = Path(path).expanduser().stat()
        return (stat.st_mtime_ns, stat.st_size, stat.st_ino)
    except (OSError, TypeError):
        return None


def auth_key(region):
    config = os.getenv("OCI_CONFIG_FILE", "~/.oci/config")
    return (
        region,
        tuple(sorted((k, v) for k, v in os.environ.items() if k.startswith("OCI_"))),
        file_stamp(config),
    )


def invalidate_auth():
    with _AUTH_LOCK:
        _AUTH_CACHE.clear()
        _SCOPE_CACHE.clear()


def auth(region: str):
    if not re.fullmatch(r"[a-z][a-z0-9]*(-[a-z0-9]+)+-[0-9]+", region):
        raise ScopeError("Use an OCI region name, not a URL.")
    key = auth_key(region)
    with _AUTH_LOCK:
        cached = _AUTH_CACHE.get(key)
        if cached:
            created, context, stamps = cached
            if time.monotonic() - created < AUTH_TTL and all(
                file_stamp(path) == stamp for path, stamp in stamps
            ):
                return context
        try:
            context = build_auth_context(AuthOptions(region=region))
        except Exception:
            raise AuthenticationError() from None
        paths = [
            context.config.get(k)
            for k in ("security_token_file", "key_file", "delegation_token_file")
        ]
        stamps = [(path, file_stamp(path)) for path in paths if path]
        if len(_AUTH_CACHE) >= 8:
            _AUTH_CACHE.clear()
        _AUTH_CACHE[key] = (time.monotonic(), context, stamps)
        return context


# Retain the testing/administrative cache-clear interface from the previous runtime.
auth.cache_clear = invalidate_auth


def configured_roots():
    roots = {
        scope_id(v.strip())
        for v in os.getenv("OCI_ALLOWED_COMPARTMENT_IDS", "").split(",")
        if v.strip()
    }
    subtrees = {
        scope_id(v.strip())
        for v in os.getenv("OCI_ALLOWED_COMPARTMENT_SUBTREES", "").split(",")
        if v.strip()
    }
    mode = os.getenv("OCI_ALLOWED_COMPARTMENT_MODE", "subtree")
    if mode not in {"exact", "subtree"}:
        raise ScopeError("Unknown compartment mode")
    return roots | subtrees, subtrees | (roots if mode == "subtree" else set())


def check_scope(compartment_id: str, region: str, *, tenancy_only: bool = False):
    scope_id(compartment_id)
    context = auth(region)
    if tenancy_only:
        if compartment_id != context.tenancy_id:
            raise ScopeError("Tenancy must match the authenticated tenancy.")
        return context
    roots, subtrees = configured_roots()
    if not roots or compartment_id in roots:
        return context
    cache_key = (auth_key(region), tuple(sorted(subtrees)), compartment_id)
    with _AUTH_LOCK:
        expiry = _SCOPE_CACHE.get(cache_key, 0)
    if expiry > time.monotonic():
        return context
    current, seen = compartment_id, set()
    identity = None
    while subtrees and current != context.tenancy_id and current not in seen and len(seen) < 32:
        seen.add(current)
        if identity is None:
            identity = client(oci.identity.IdentityClient, region)
        compartment = identity.get_compartment(current).data
        current = scope_id(compartment.compartment_id)
        if current in subtrees:
            with _AUTH_LOCK:
                if len(_SCOPE_CACHE) >= 4096:
                    _SCOPE_CACHE.clear()
                _SCOPE_CACHE[cache_key] = time.monotonic() + AUTH_TTL
            return context
    raise ScopeError("Compartment is outside the configured roots and subtrees.")


def require_subtree(compartment_id, region):
    context = check_scope(compartment_id, region)
    roots, subtrees = configured_roots()
    if roots and compartment_id in roots and compartment_id not in subtrees:
        raise ScopeError("Exact compartment mode cannot include descendants")
    return context


def descendant_rows(compartment_id, region):
    context = require_subtree(compartment_id, region)
    identity = client(oci.identity.IdentityClient, region)
    entries, seen, cursor = [], set(), None
    for _ in range(100):
        response = identity.list_compartments(
            context.tenancy_id,
            access_level="ACCESSIBLE",
            compartment_id_in_subtree=True,
            limit=100,
            page=cursor,
        )
        entries.extend(response.data)
        cursor = response.headers.get("opc-next-page")
        if not cursor:
            break
        if cursor in seen:
            raise ScopeError("Repeated compartment cursor")
        seen.add(cursor)
    else:
        raise ScopeError("Compartment discovery exceeded its bound")
    selected = {compartment_id}
    for _ in range(32):
        expanded = selected | {row.id for row in entries if row.compartment_id in selected}
        if expanded == selected:
            return sorted(
                (row for row in entries if row.id in selected and row.id != compartment_id),
                key=lambda row: row.id,
            )
        selected = expanded
    raise ScopeError("Compartment depth exceeded its bound")


def descendant_ids(compartment_id, region):
    return [compartment_id, *(row.id for row in descendant_rows(compartment_id, region))]


def client(factory, region: str):
    context = auth(region)
    config = {**context.config, "additional_user_agent": f"oci-readonly-mcp/{__version__}"}
    kwargs = {"timeout": (5, 25), "retry_strategy": oci.retry.NoneRetryStrategy()}
    if context.signer is not None:
        kwargs["signer"] = context.signer
    return factory(config, **kwargs)


def guarded(fn):
    def execute(*args, **kwargs):
        try:
            for attempt in range(2):
                try:
                    return fn(*args, **kwargs)
                except oci.exceptions.ServiceError as exc:
                    if exc.status != 401 or attempt:
                        raise
                    invalidate_auth()
        except ScopeError:
            return {
                "ok": False,
                "error": {
                    "kind": "invalid_scope",
                    "message": "Region, OCID or compartment allowlist rejected the scope.",
                },
            }
        except AuthenticationError:
            return {
                "ok": False,
                "error": {
                    "kind": "authentication",
                    "message": "Local OCI authentication configuration is unavailable or invalid.",
                },
            }
        except (ValueError, TypeError):
            return {
                "ok": False,
                "error": {
                    "kind": "invalid_input",
                    "message": "Input format or bounds are invalid.",
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
                    "message": "OCI rejected the read for this identity, region and resource scope.",
                },
            }
        except Exception:
            return {
                "ok": False,
                "error": {
                    "kind": "configuration_or_transport",
                    "message": "Authentication or connectivity failed; raw exception details are suppressed.",
                },
            }

    @functools.wraps(fn)
    async def wrapped(*args, **kwargs):
        result = await anyio.to_thread.run_sync(functools.partial(execute, *args, **kwargs))
        result.setdefault('source', 'oci:tool:' + fn.__name__)
        result.setdefault('trust', 'account-controlled')
        result['complete'] = bool(result.get('ok')) and not result.get('truncated', False) and 'truncated' not in result.get('flags', [])
        return result

    return wrapped


def shaped(rows, kind: str):
    # Excludes tags, metadata, IPs, URLs and object bodies; names remain untrusted data.
    result = []
    for row in rows:
        data = row if isinstance(row, dict) else oci.util.to_dict(row)

        result.append({key: data[key] for key in FIELDS[kind] if key in data})
    return result


SOURCES = {
    'regions': 'oci:identity:list_region_subscriptions',
    'compartments': 'oci:identity:list_compartments',
    'instances': 'oci:compute:list_instances',
    'vcns': 'oci:network:list_vcns', 'subnets': 'oci:network:list_subnets',
    'network_security_groups': 'oci:network:list_network_security_groups',
    'buckets': 'oci:object_storage:list_buckets', 'search': 'oci:resource_search:search_resources',
    'limit_services': 'oci:limits:list_services', 'limit_values': 'oci:limits:list_limit_values',
    'costs': 'oci:usage_api:request_summarized_usages', 'audit': 'oci:audit:list_events',
    'work_requests': 'oci:work_requests:list_work_requests',
    'whoami': 'oci:identity:get_tenancy+list_region_subscriptions',
}


def page_result(response, kind: str, page_size: int, *, collection: bool = False):
    if not 1 <= page_size <= 100:
        raise ValueError("Invalid page size")
    rows = response.data.items if collection else response.data
    next_cursor = response.headers.get("opc-next-page") or None
    # OCI is expected to respect limit. Never silently skip oversized response rows.
    oversized = len(rows) > page_size
    result = {
        "ok": True,
        **envelope(shaped(rows[:page_size], kind), source=SOURCES.get(kind, 'oci:' + kind + ':read'),
                   kind=kind, complete=not (next_cursor or oversized)),
        "count": min(len(rows), page_size),
        "truncated": bool(next_cursor) or oversized,
        "next_cursor": None if oversized else next_cursor,
        "pagination_error": "OCI returned more rows than requested; continuation is unavailable."
        if oversized
        else None,
    }

    result["complete"] = result["complete"] and "truncated" not in result["flags"]
    return result

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
    compartment_id: Scope,
    region: Region,
    page_size: PageSize = 50,
    cursor: Cursor = None,
    include_subtree: bool = False,
) -> dict:
    """Discover child compartments. Subtree reads require a permitted subtree scope."""
    context = (
        require_subtree(compartment_id, region)
        if include_subtree
        else check_scope(compartment_id, region)
    )
    if include_subtree and compartment_id != context.tenancy_id:
        # OCI only accepts its native subtree switch at the tenancy root.
        after = ""
        if cursor:
            if not cursor.startswith("subtree:"):
                raise ValueError("Expected a subtree cursor")
            after = scope_id(cursor.removeprefix("subtree:"))
        rows = [row for row in descendant_rows(compartment_id, region) if row.id > after]
        selected = rows[:page_size]
        result = synthetic_page(selected, "compartments", page_size)
        result["truncated"] = len(rows) > page_size
        result["next_cursor"] = "subtree:" + selected[-1].id if result["truncated"] else None

        return result
    response = client(oci.identity.IdentityClient, region).list_compartments(
        compartment_id,
        access_level="ACCESSIBLE",
        compartment_id_in_subtree=include_subtree,
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
def oci_limit_services(tenancy_id: Scope, region: Region, page_size: PageSize = 50,
                       cursor: Cursor = None) -> dict:
    """List limit services for the authenticated tenancy."""
    check_scope(tenancy_id, region, tenancy_only=True)
    response = client(oci.limits.LimitsClient, region).list_services(tenancy_id, limit=page_size, page=cursor)
    return page_result(response, "limit_services", page_size)


@mcp.tool(annotations=READ)
@guarded
def oci_limit_values(tenancy_id: Scope, region: Region,
                     service_name: Annotated[str, Field(pattern=r"^[a-z0-9-]+$", max_length=100)],
                     page_size: PageSize = 50, cursor: Cursor = None) -> dict:
    """List configured limit values for one service; limits do not measure capacity."""
    check_scope(tenancy_id, region, tenancy_only=True)
    response = client(oci.limits.LimitsClient, region).list_limit_values(tenancy_id, service_name, limit=page_size, page=cursor)
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
    compartment_depth: Annotated[int, Field(ge=1, le=6)] = 1,
    include_descendants: bool = False,
    all_regions: bool = False,
) -> dict:
    """Reported costs, UTC dates, end exclusive, max 31 days. Explicit descendant and all-region switches; compartment_depth controls grouping, not authorization. IAM visibility can omit costs."""
    context = check_scope(compartment_id, region)
    start = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    end = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    if not timedelta(0) < end - start <= timedelta(days=31):
        raise ValueError("Cost window must be between 1 and 31 days")
    if not context.tenancy_id:
        raise ScopeError("Authentication must resolve the tenancy")
    if not 1 <= compartment_depth <= 6:
        raise ValueError("Invalid compartment depth")
    compartments = (
        descendant_ids(compartment_id, region) if include_descendants else [compartment_id]
    )
    models = oci.usage_api.models
    scope_filter = models.Filter(
        operator="OR",
        dimensions=[models.Dimension(key="compartmentId", value=value) for value in compartments],
    )
    dimensions = [] if all_regions else [models.Dimension(key="region", value=region)]
    details = models.RequestSummarizedUsagesDetails(
        tenant_id=context.tenancy_id,
        time_usage_started=start,
        time_usage_ended=end,
        granularity="DAILY",
        query_type="COST",
        is_aggregate_by_time=True,
        group_by=["service", "currency", "compartmentId"],
        compartment_depth=compartment_depth,
        filter=models.Filter(
            operator="AND",
            dimensions=dimensions
            + (
                []
                if include_descendants
                else [models.Dimension(key="compartmentId", value=compartment_id)]
            ),
            filters=[scope_filter] if include_descendants else None,
        ),
    )
    response = client(oci.usage_api.UsageapiClient, region).request_summarized_usages(
        details, limit=page_size, page=cursor
    )
    result = page_result(response, "costs", page_size, collection=True)

    result["excluded_scopes"] = ([] if include_descendants else ["descendant_compartments"]) + (
        [] if all_regions else ["other_regions"]
    )
    result["compartment_depth"] = compartment_depth
    return result


# Diagnostics use fixed SDK operations and narrowly projected response fields.
FIELDS.update(
    {
        "work_requests": (
            "id",
            "operation_type",
            "status",
            "compartment_id",
            "percent_complete",
            "time_accepted",
            "time_finished",
        ),
        "work_errors": ("code", "message", "timestamp"),
        "work_logs": ("message", "timestamp"),
        "alarms": ("id", "display_name", "severity", "status", "timestamp_triggered"),
        "alarm_history": ("summary", "timestamp", "timestamp_triggered"),
        "audit": ("event_time", "event_name", "principal_id", "resource_id", "status"),
        "metrics": ("timestamp", "value", "name", "resource_id"),
        "whoami": (
            "auth_type",
            "profile",
            "config_file",
            "region",
            "tenancy_id",
            "tenancy_name",
            "allowlist_size",
            "version",
        ),
        "prices": ("part_number", "display_name", "metric", "currency", "model", "value"),
    }
)
ResourceId = Annotated[
    str,
    Field(pattern=r"^ocid1\.[a-z0-9_-]+\.[a-z0-9]+\.[a-z0-9-]*\.[A-Za-z0-9_-]+$", max_length=255),
]
Timestamp = Annotated[str, Field(max_length=40, description="RFC3339 with timezone.")]


def bounded_window(start_time, end_time):
    if not isinstance(start_time, str) or not isinstance(end_time, str):
        raise ValueError("Both timestamps are required")
    start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
    end = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
    if (
        start.tzinfo is None
        or end.tzinfo is None
        or not timedelta(0) < end - start <= timedelta(hours=24)
    ):
        raise ValueError("Window must be positive and at most 24 hours with timezones")
    return start, end


def synthetic_page(rows, kind, size=100, cursor=None):
    from types import SimpleNamespace

    return page_result(SimpleNamespace(data=rows, headers={"opc-next-page": cursor}), kind, size)


def redact_message(value):
    from .redaction import redact

    return redact(value) if isinstance(value, str) else value


def redact_rows(response):
    rows = []
    for value in response.data:
        data = value if isinstance(value, dict) else oci.util.to_dict(value)
        rows.append(
            {
                key: redact_message(val)
                for key, val in data.items()
                if key in {"code", "message", "summary", "timestamp", "timestamp_triggered"}
            }
        )
    from types import SimpleNamespace

    return SimpleNamespace(data=rows, headers=response.headers)


@mcp.tool(annotations=READ)
@guarded
def oci_whoami() -> dict:
    """Inspect active identity, scope and region subscriptions; never key material."""
    try:
        initial = build_auth_context(AuthOptions())
    except Exception:
        raise AuthenticationError() from None
    region = initial.region or initial.config.get("region")
    context = auth(region)
    if not context.tenancy_id:
        raise AuthenticationError()
    identity = client(oci.identity.IdentityClient, region)
    tenancy = identity.get_tenancy(context.tenancy_id).data
    subscriptions = identity.list_region_subscriptions(context.tenancy_id)
    roots, _ = configured_roots()
    row = {
        "auth_type": getattr(context.auth_type, "value", str(context.auth_type)),
        "profile": context.profile_name,
        "config_file": os.getenv("OCI_CONFIG_FILE", "~/.oci/config"),
        "region": region,
        "tenancy_id": context.tenancy_id,
        "tenancy_name": tenancy.name,
        "allowlist_size": len(roots),
        "version": __version__,
    }
    result = synthetic_page([row], "whoami", 1)
    result["regions"] = page_result(subscriptions, "regions", 100)
    return result


@mcp.tool(annotations=READ)
@guarded
def oci_work_requests(
    compartment_id: Scope,
    region: Region,
    work_request_id: ResourceId | None = None,
    page_size: PageSize = 50,
    cursor: Cursor = None,
    detail: Literal["summary", "errors", "logs"] = "summary",
) -> dict:
    """List common work requests, or inspect one request's status, errors or logs."""
    check_scope(compartment_id, region)
    work = client(oci.work_requests.WorkRequestClient, region)
    if not work_request_id:
        if detail != "summary":
            raise ValueError("Details need a work request ID")
        return page_result(
            work.list_work_requests(compartment_id, limit=page_size, page=cursor),
            "work_requests",
            page_size,
        )
    response = work.get_work_request(work_request_id)
    if response.data.compartment_id != compartment_id:
        raise ScopeError("Work request is outside the requested compartment")
    if detail == "summary":
        return synthetic_page([response.data], "work_requests", page_size)
    if detail == "errors":
        response = work.list_work_request_errors(work_request_id, limit=page_size, page=cursor)
        return page_result(redact_rows(response), "work_errors", page_size)
    if detail == "logs":
        response = work.list_work_request_logs(work_request_id, limit=page_size, page=cursor)
        return page_result(redact_rows(response), "work_logs", page_size)
    raise ValueError("Unknown detail")


@mcp.tool(annotations=READ)
@guarded
def oci_alarm_status(
    compartment_id: Scope,
    region: Region,
    alarm_id: ResourceId | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    page_size: PageSize = 50,
    cursor: Cursor = None,
) -> dict:
    """List alarm status; an alarm ID and bounded timestamps select its history."""
    check_scope(compartment_id, region)
    monitoring = client(oci.monitoring.MonitoringClient, region)
    if alarm_id:
        start, end = bounded_window(start_time, end_time)
        if monitoring.get_alarm(alarm_id).data.compartment_id != compartment_id:
            raise ScopeError("Alarm is outside the requested compartment")
        response = monitoring.get_alarm_history(
            alarm_id,
            timestamp_greater_than_or_equal_to=start,
            timestamp_less_than=end,
            limit=page_size,
            page=cursor,
        )
        from types import SimpleNamespace

        response = SimpleNamespace(data=response.data.entries, headers=response.headers)
        return page_result(redact_rows(response), "alarm_history", page_size)
    if start_time or end_time:
        raise ValueError("History timestamps require an alarm ID")
    return page_result(
        monitoring.list_alarms_status(compartment_id, limit=page_size, page=cursor),
        "alarms",
        page_size,
    )


@mcp.tool(annotations=READ)
@guarded
def oci_audit_events(
    compartment_id: Scope,
    region: Region,
    start_time: Timestamp,
    end_time: Timestamp,
    page_size: PageSize = 50,
    cursor: Cursor = None,
) -> dict:
    """Read at most one Audit page over a window of up to 24 hours; excludes payloads."""
    check_scope(compartment_id, region)
    start, end = bounded_window(start_time, end_time)
    response = client(oci.audit.AuditClient, region).list_events(
        compartment_id, start, end, page=cursor
    )
    entries = []
    for event in response.data:
        data = oci.util.to_dict(event)
        details = data.get("data") or {}
        entries.append(
            {
                "event_time": data.get("event_time"),
                "event_name": details.get("event_name"),
                "resource_id": details.get("resource_id"),
                "principal_id": (details.get("identity") or {}).get("principal_id"),
                "status": (details.get("response") or {}).get("status"),
            }
        )
    result = synthetic_page(entries, "audit", page_size, response.headers.get("opc-next-page"))

    return result


METRIC_TEMPLATES = {
    "cpu_utilization": ("oci_computeagent", "CpuUtilization"),
    "memory_utilization": ("oci_computeagent", "MemoryUtilization"),
}


@mcp.tool(annotations=READ)
@guarded
def oci_metrics(
    compartment_id: Scope,
    region: Region,
    start_time: Timestamp,
    end_time: Timestamp,
    template: Literal["cpu_utilization", "memory_utilization"] = "cpu_utilization",
    resource_id: ResourceId | None = None,
) -> dict:
    """Read fixed compute-agent metric templates; max 24 hours and 500 datapoints."""
    check_scope(compartment_id, region)
    start, end = bounded_window(start_time, end_time)
    namespace, metric = METRIC_TEMPLATES[template]
    selector = ""
    if resource_id:
        if not re.fullmatch(r"ocid1\.instance\.[a-z0-9]+\.[a-z0-9-]*\.[A-Za-z0-9_-]+", resource_id):
            raise ValueError("Expected an instance OCID")
        selector = '{resourceId="' + resource_id + '"}'
    details = oci.monitoring.models.SummarizeMetricsDataDetails(
        namespace=namespace,
        query=metric + "[5m]" + selector + ".mean()",
        start_time=start,
        end_time=end,
        resolution="5m",
    )
    response = client(oci.monitoring.MonitoringClient, region).summarize_metrics_data(
        compartment_id, details
    )
    points, total = [], 0
    for stream in response.data:
        for point in stream.aggregated_datapoints or []:
            total += 1
            if len(points) < 500:
                points.append(
                    {
                        "timestamp": str(point.timestamp),
                        "value": point.value,
                        "name": stream.name,
                        "resource_id": (stream.dimensions or {}).get("resourceId"),
                    }
                )
    return {
        "ok": True,
        **envelope(shaped(points, "metrics"), source='oci:monitoring:summarize_metrics_data',
                   kind='metrics', complete=total <= 500),
        "count": len(points),
        "truncated": total > 500,
        "next_cursor": None,
    }


PRICE_URL = "https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/"


def fetch_prices(part_number, currency):
    import urllib.parse
    import urllib.request

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    request = urllib.request.Request(
        PRICE_URL
        + "?"
        + urllib.parse.urlencode({"partNumber": part_number, "currencyCode": currency}),
        headers={"Accept": "application/json"},
    )
    # urllib does not read OCI credentials or .netrc; fixed origin, no redirects.
    with urllib.request.build_opener(NoRedirect).open(request, timeout=15) as response:
        data = response.read(2_000_001)
        if len(data) > 2_000_000:
            raise ValueError("Public price response exceeds bound")
        return json.loads(data)


@mcp.tool(annotations=READ)
@guarded
def oci_price_lookup(
    part_number: Annotated[str, Field(pattern=r"^B[0-9]{4,9}$")],
    currency: Annotated[str, Field(pattern=r"^[A-Z]{3}$")] = "USD",
) -> dict:
    """Look up one public Oracle SKU without credentials; list prices are not a quote."""
    if not re.fullmatch(r"B[0-9]{4,9}", part_number) or not re.fullmatch(r"[A-Z]{3}", currency):
        raise ValueError("Invalid SKU or currency")
    response = fetch_prices(part_number, currency)
    rows = []
    for product in response["items"] or []:
        if product.get("partNumber") != part_number:
            continue
        for prices in product.get("currencyCodeLocalizations", product.get("prices", [])):
            if prices.get("currencyCode") != currency:
                continue
            for price in prices.get("prices", []):
                rows.append(
                    {
                        "part_number": part_number,
                        "display_name": product.get("displayName"),
                        "metric": product.get("metricName"),
                        "currency": currency,
                        "model": price.get("model"),
                        "value": price.get("value"),
                    }
                )
    result = synthetic_page(rows, "prices", 100)
    result["truncated"] = result["truncated"] or bool(response.get("hasMore"))
    result["source"] = PRICE_URL
    result["trust"] = "public-oracle-catalog"

    return result


def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
