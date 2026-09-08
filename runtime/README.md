# OCI read-only MCP runtime

Independent adapter, not an Oracle product. Nine fixed tools expose OCI inventory,
reported costs and configured limits over stdio. This is a small operational subset,
not coverage of every Oracle cloud, database, Fusion or NetSuite product.

Requires `uv` and Python 3.13 (uv can provision Python). From the plugin directory:

```bash
uv sync --frozen --project runtime
uv run --frozen --project runtime oci-readonly-mcp
uv run --frozen --project runtime oci-readonly-smoke
uv run --frozen --project runtime pytest -q tests/test_runtime.py
```

Portable Claude plugin launcher:

```json
{
  "mcpServers": {
    "oci-readonly": {
      "command": "uv",
      "args": ["run", "--frozen", "--project", "${CLAUDE_PLUGIN_ROOT}/runtime", "oci-readonly-mcp"]
    }
  }
}
```

For other MCP hosts, replace `${CLAUDE_PLUGIN_ROOT}` with the installed plugin path.
No credentials or local tenancy IDs belong in a published manifest. The first run
downloads locked dependencies; installation therefore requires package network access.

## Authentication and scope

Authentication is delegated to Oracle's `oracle-mcp-common==0.1.3`, preserving its
profile selection and signer handling. Default: `~/.oci/config`, profile `DEFAULT`.
Environment settings:

| Setting | Meaning |
| --- | --- |
| `OCI_CONFIG_FILE` | Local OCI configuration file |
| `OCI_CONFIG_PROFILE` | Profile, default `DEFAULT` |
| `OCI_MCP_AUTH_TYPE` | `auto`, `api_key`, `security_token`, `instance_principal`, `resource_principal`, or other modes supported by the shared library |
| `OCI_ALLOWED_COMPARTMENT_IDS` | Optional comma-separated exact compartment/tenancy OCIDs allowed for compartment tools |

API keys remain in local files. Session tokens, instance principals and resource
principals are resolved by the shared library; this adapter does not accept secrets
as tool arguments. Principal modes have not been live-tested in this workstation.
Every cloud tool requires an explicit OCI `region` and compartment or tenancy OCID.
That region overrides the profile region. Authentication contexts are cached per
region for the process lifetime: restart after changing configuration or environment.

When the allowlist is absent, explicitly selected compartments are limited by the
principal's OCI IAM permissions. When present, matching is exact, with no implicit
permission to read descendant resources. `oci_compartments` discovers immediate
child metadata of the selected parent; it does not confer access inside the children.
Region subscriptions and service limits are tenancy metadata tools and separately
require the authenticated tenancy ID; the compartment allowlist does not filter them.
Use IAM policies as the authoritative access boundary. MCP hints describe behavior
but are not an authorization system.

## Tools and limits

| Tool | Data returned |
| --- | --- |
| `oci_regions` | Region subscriptions of the authenticated tenancy |
| `oci_compartments` | Immediate child compartments, no recursive scan |
| `oci_instances` | Compute IDs, names, lifecycle, shape, AD and creation time |
| `oci_network_inventory` | One of VCNs, subnets or network security groups |
| `oci_buckets` | Bucket metadata, no object listing or object contents |
| `oci_resource_search` | Fixed exact-compartment resource search; no raw query input |
| `oci_limit_services` | Service names for limit lookup |
| `oci_limit_values` | Configured service limit values, not usage or guaranteed capacity |
| `oci_cost_summary` | Reported costs by service/currency, exact compartment and region |

Each tool makes a single inventory page request (buckets additionally resolves the
namespace), with `page_size` 1–100, default 50. Results include `count`, `truncated`
and `next_cursor`. Pass a cursor only to the same tool with unchanged scope, filters
and page size. Never describe a truncated page as a complete inventory. Regions are
an unpaginated API: increase `page_size` to see all subscribed regions. If an API
returns more than the requested limit, rows remain capped and `pagination_error`
explains that continuation cannot safely skip the discarded rows.

Costs accept UTC `YYYY-MM-DD` dates with an exclusive end date and a maximum 31-day
window. Costs exclude child compartments and other regions. Reported costs can lag;
the adapter does not calculate a cross-currency total or estimate a future invoice.
Resource Search is eventually consistent and does not index every OCI resource type.

Outputs use a fixed field allowlist: metadata, tags, SSH/user data, addresses,
object bodies and raw exceptions are excluded. Operational resource IDs and names
are retained for follow-up reads; treat these results as private account metadata,
not anonymized publication material. Error results expose only a fixed description,
category, HTTP status and retryability. Tools cannot execute CLI commands, arbitrary
SDK methods, arbitrary SQL, infrastructure mutations or instance-agent commands.
The SDK uses a 5-second connection timeout, 25-second read timeout and no retries.

## Live smoke

Only run against a tenancy you are authorized to inspect:

```bash
OCI_CONFIG_PROFILE=DEFAULT uv run --frozen --project runtime oci-readonly-smoke --live --region us-chicago-1
```

The smoke authenticates locally, discovers the tenancy ID without printing it,
then reads one small page for each operation (all region subscriptions). Set
`OCI_SMOKE_COMPARTMENT_ID` to inspect a specific compartment; otherwise it reads
root-compartment resources. It prints only tool names, pass/fail, counts,
truncation flags and sanitized error categories/statuses, never inventory or cursors.
Its asynchronous protocol reads have an overall deadline (`--timeout`, default 180
seconds) and close the child process on failure, avoiding blocking `readline()` loops.
