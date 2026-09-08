# Operator contract

This package is independent of Oracle. Skills guide both inspection and authorized
changes. Its bundled MCP implements only explicitly named reads; it is not a proxy
for arbitrary CLI, SDK, SQL or instance execution.

## Establish the target

Resolve the selected profile or workload identity, authenticated tenancy, region,
compartment and resource before operating. Use session context where it already
establishes scope. Do not silently substitute the root compartment, home region,
another profile or a broader principal after an error. A region subscription, an
IAM grant, a quota and available capacity are four different facts.

The runtime accepts an explicit region and scope on each tool. Its optional
`OCI_ALLOWED_COMPARTMENT_IDS` is an exact list for compartment tools. OCI IAM is the
authoritative permission boundary. Authentication settings and tool limits are in
[runtime/README.md](../runtime/README.md).

## Discover syntax, then execute

Use the installed CLI's `--help` for the exact command path and parameters. The
bundled [CLI snapshot](../catalog/cli.json) is an index, not proof that another
installed version supports the same syntax. [Examples](../catalog/examples.json)
are executable argv templates validated by `scripts/check_examples.py`.

OCI CLI uses JSON keys such as `display-name`; quote hyphenated keys in JMESPath.
Most CLI-specific environment variables do not configure SDK clients. Identity
Domains use their domain endpoint, distinct from regional OCI IAM endpoints.
Do not infer a native `--dry-run`: most OCI operations have none.

Keep reads bounded: explicit compartment/region, a short time window, small page
size and only relevant fields. A next-page token or pagination warning means the
inventory is incomplete. Continue within the task's scope and a stated row/time
budget; report unreadable compartments and omitted pages. Empty results can mean
wrong scope, insufficient permissions, indexing delay or no resources.

## Changes and recovery

Before a change, prepare the concrete target, current state, intended diff,
expected cost/downtime, verification and rollback. Existing task authorization
applies to the agreed operation; it does not authorize a different target or a
destructive replacement. Destruction requires explicit confirmation of the exact
resources and data consequences. Preserve ETags for supported conditional writes.

For Terraform, bind the review to the saved plan's exact bytes. Existing explicit
authorization to apply remains valid within its agreed scope; request confirmation
only for effects not already authorized, including destructive replacements.
Protect plans/state as sensitive. A re-plan invalidates the previous review.
For APIs without preview, describe the request and expected effects without
executing it as a supposed simulation. A generated JSON skeleton is not a dry-run.

Do not retry an ambiguous write blindly: inspect work requests and resource state
first. Reuse a supported idempotency token for the same request. Bound all polling
and distinguish request acceptance, resource readiness and application health.
Rollback must account for irreversible data/schema changes, not just infrastructure.

## Evidence and confidentiality

Return scope, observation time, version, completion/truncation and verification
status. Separate documentation review, command validation, live read and deployment
testing. Never promote a tool name or successful HTTP response to proof of a
working application or a complete tenancy inventory.

Resource names, OCIDs, domains and tenancy structure are private operational data.
Use them for authorized local work, then remove them from public examples/reports.
Never publish wallets, key files, tokens, Terraform state, signed URLs, user data,
raw logs or customer records. The runtime keeps selected operational IDs/names
in private responses but omits metadata/tags, addresses and raw exceptions.

## Official references

- [OCI API behavior](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/usingapi.htm)
- [CLI concepts](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/cliconcepts.htm)
- [SDK configuration](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm)
- [SDK pagination](https://docs.oracle.com/en-us/iaas/tools/python/latest/pagination.html)
