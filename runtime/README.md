# OCI read-only MCP runtime

This independent adapter exposes fixed OCI reads over MCP stdio. Inventory, diagnostics,
reported costs and public SKU prices use bounded results and fixed field projections.
The current mechanisms, commands, known limitations and host installation instructions
are documented in [foundation.md](../docs/foundation.md).

From the repository root:

```bash
uv sync --frozen --project runtime
uv run --frozen --project runtime oci-readonly-smoke
uv run --frozen --project runtime pytest -q tests
```

The offline smoke lists the complete annotated tool surface and reports schema size.
Its `schema_tokens_estimate` is characters divided by four, rounded up; it is an estimate,
not a tokenizer measurement. Credentials are unnecessary for tool discovery.

For a live, read-only smoke, select the intended profile and region:

```bash
OCI_CONFIG_PROFILE=DEFAULT uv run --frozen --project runtime oci-readonly-smoke --live --region "$OCI_REGION"
```

The smoke prints counts, truncation and sanitized statuses, never resource names,
identifiers, cursors or credentials. Empty telemetry does not establish zero utilization.
A failed request remains a failure; IAM restrictions and service availability can change
live results. Work-request detail/history branches are covered offline even when the
selected tenancy has no relevant resources.

## Authentication and scope

The locked `oracle-mcp-common` dependency resolves authentication. `OCI_CONFIG_FILE`,
`OCI_CONFIG_PROFILE` and `OCI_MCP_AUTH_TYPE` select the local configuration.
`oci_whoami` reports identity and effective configuration without key material.

Contexts expire on the cache TTL or credential-file changes. A service response with
status 401 clears cached auth and retries the fixed read once. The adapter does not run
session authentication or refresh commands; an expired token must be renewed outside
this server. SDK work runs in worker threads so concurrent MCP requests remain responsive.

`OCI_ALLOWED_COMPARTMENT_IDS` permits those roots and descendants by default.
`OCI_ALLOWED_COMPARTMENT_MODE=exact` restricts those entries to exact matching.
`OCI_ALLOWED_COMPARTMENT_SUBTREES` explicitly permits subtree roots in either mode.
Descendants are checked using OCI parent relationships, never a textual OCID prefix.
An absent allowlist leaves scope enforcement to IAM. An ancestry lookup failure does not
grant access. Tenancy identity, regions and limits are separate tenancy metadata reads.

Costs default to one compartment and one region. `include_descendants` enumerates
accessible descendants; `all_regions` removes the region filter. `compartment_depth`
controls grouping and does not authorize wider access. Responses declare excluded scopes,
and IAM-limited discovery can still omit descendant costs. No cross-currency total is formed.

## Tool contract

15 shipped tools (14 credentialed + oci_price_lookup, credential-free).
`oci_limit_services` discovers service names; `oci_limit_values` reads configured
values for one service. Results carry `source`, `trust`, and `complete`; completeness
is relative to the requested scope/page and is false for truncated data. Field
flags are advisory, and suspicious values remain visible. The shared sanitizer is
included from scripts/lib/sanitize.py when building the runtime wheel.

Most inventory tools return one page with `count`, `truncated`, `next_cursor` and
`pagination_error`. An oversized API page is capped and loses its cursor rather than
silently skipping discarded rows. Audit has no server-side `limit`; use a smaller time
window if its page overflows. Metrics use a fixed template set and an overall datapoint
cap. Missing metrics are not zero usage. Resource Search is eventually consistent.

Names and diagnostic messages are untrusted account data, not instructions. Output
fields exclude tags, metadata, addresses, object contents and arbitrary request bodies.
Names are bounded, control characters are removed, and work-request messages are redacted.
The public price lookup uses a fixed Oracle endpoint, carries no OCI credentials and
refuses redirects. Prices are public list prices, not negotiated quotes or capacity claims.

The runtime never executes CLI, SQL, arbitrary SDK methods or tenancy mutations.
IAM remains the access boundary; MCP annotations describe behavior, not authorization.
