# OCI Agent Skills

Oracle cloud engineering workflows for Claude Code and Codex: 16 focused skills,
a reproducible CLI/SDK catalog, a product/control-plane map and a small read-only
MCP adapter. Independent community project; not affiliated with Oracle.

The package helps agents inspect, design and make authorized changes across OCI,
database/APEX, DevOps, Kubernetes, infrastructure as code, AI/data and reliability.
Its bundled MCP exposes nine fixed read tools rather than the entire OCI API.

## Start here

Prerequisites: `uv`, Python 3.13 for the MCP (uv can provision it), and an existing
OCI profile or supported principal. CLI discovery/examples additionally require
OCI CLI in the Python environment used for those scripts. Credentials stay local.

```bash
uv sync --frozen --project runtime
uv run --frozen --project runtime oci-readonly-smoke
```

The first command installs locked dependencies; the second verifies the MCP stdio
handshake and tool schemas without contacting OCI. For an authorized live read:

```bash
OCI_CONFIG_PROFILE=DEFAULT uv run --frozen --project runtime oci-readonly-smoke --live --region REGION_NAME
```

Replace `REGION_NAME` with the selected region. This smoke defaults to root-
compartment metadata; set `OCI_SMOKE_COMPARTMENT_ID` for a narrower target. Tool
calls themselves require explicit scope. See [runtime configuration](runtime/README.md)
for authentication, compartment allowlists, projection, pagination and limits.

## Use with an agent

Keep the **complete plugin directory**: skills link to shared docs and catalogs.
Copying only `skills/` loses those references. Both host manifests point to these
same skill folders; no always-on prompt injection or mandatory router hook is used.

Claude Code supports loading the local checkout:

```bash
claude --plugin-dir /absolute/path/to/oci-agent-skills
```

Its root `.mcp.json` uses `CLAUDE_PLUGIN_ROOT` to find the runtime.

Codex packaging is `.codex-plugin/plugin.json`. Its inline `mcpServers` configuration
uses a direct server map and `cwd: "."`, resolved against the installed plugin root,
so it does not depend on Claude variable expansion. This resolution was checked
against the [installed Codex 0.153.4 parser](https://github.com/openai/codex/blob/rust-v0.153.4/codex-rs/codex-mcp/src/plugin_config.rs).
Host installation still uses the host's configured marketplace/plugin mechanism;
this checkout does not register a marketplace or change global host configuration.
The Codex manifest and launcher are validated; interactive host pickup is not claimed
as tested. See [official packaging docs](https://developers.openai.com/plugins/build/plugins).

For any other MCP host, configure `uv run --frozen --project
/absolute/path/to/oci-agent-skills/runtime oci-readonly-mcp` as a stdio server.

Example requests:

- “Inspect this compartment's instances and network dependencies; report incomplete pages.”
- “Explain this month's cost increase using equal completed periods and the same scope.”
- “Plan an APEX release on the existing Autonomous database, including schema rollback.”
- “Investigate this OKE endpoint failure after a networking change.”

## What is included

| Area | Entry point |
| --- | --- |
| Control-plane routing | [oci-navigator](skills/oci-navigator/SKILL.md) |
| IAM, compute/network, storage | [identity](skills/oci-identity/SKILL.md), [compute/network](skills/oci-compute-network/SKILL.md), [storage](skills/oci-storage/SKILL.md) |
| Delivery | [OKE](skills/oci-oke/SKILL.md), [DevOps](skills/oci-devops/SKILL.md), [IaC](skills/oci-iac/SKILL.md), [SDK](skills/oci-sdk/SKILL.md) |
| Operations | [observability](skills/oci-observability/SKILL.md), [FinOps](skills/oci-finops/SKILL.md), [security](skills/oci-security/SKILL.md), [reliability](skills/oci-reliability/SKILL.md) |
| Database/application/data | [database](skills/oracle-database/SKILL.md), [APEX](skills/oracle-apex/SKILL.md), [AI/data](skills/oci-ai-data/SKILL.md), [multicloud/enterprise](skills/oracle-multicloud-enterprise/SKILL.md) |
| Research synthesis | [product map](docs/oracle-product-map.md), [SDK/DevOps](docs/sdk-and-devops.md), [audit and provenance](docs/audit.md) |
| Machine discovery | [CLI](catalog/cli.json), [Python SDK](catalog/sdk.json), [products](catalog/products.json), [read examples](catalog/examples.json) |

## Verification, 2026-09-08

- Both plugin manifests validate; all 16 skill frontmatters and local references validate.
- Nine MCP tools / eleven operation variants passed live read smoke; actual cursor
  continuation was checked. Authentication tested live: local API-key profile.
- 33 CLI examples validate offline; 31 passed live reads. Container registry returned
  HTTP 403 and Cloud Guard HTTP 404; neither was relabeled empty or retried in a broader
  scope. [Sanitized results](docs/validation-cli.json).
- All 53 command paths shown with `--help` were checked against installed CLI 3.91.0.
- 44 regression tests cover scope, paging, projected responses,
  error handling, protocol startup and OCI CLI's successful empty-output behavior.
  Both bundled host launch configurations also start over stdio without credentials;
  this checks executable/config behavior, not interactive host installation.

Regenerate the inventory using the Python interpreter **inside the OCI CLI install**:

```bash
python scripts/inventory.py --output catalog
python scripts/check_examples.py
```

That interpreter must be able to import `oci_cli` and `oci`; the MCP runtime has a
different dependency set. The snapshot records CLI 3.91.0 / SDK 2.185.0: 174 root
commands (including setup/session utilities), 9,145 leaf command paths, 170 SDK
service packages, 322 client classes and 8,198 public methods. These are discovery
counts, not a product count or a guarantee of callable endpoints. Optional
`oci.addons` did not import and is explicitly recorded. The runtime pins SDK 2.185.1.

Run the regression suite:

```bash
uv run --frozen --project runtime pytest -q tests
```

The live CLI checker requires explicit opt-in and scope; it limits each call to
one small page and prints sanitized statuses:

```bash
python scripts/check_examples.py --live --profile DEFAULT --region REGION_NAME
```

This checker defaults to root-compartment reads. Use `--compartment-id` or
`OCI_SMOKE_COMPARTMENT_ID` for narrower compartment operations. Tenancy metadata
and the `cost-usage` example remain tenancy-wide; costs include other resource
regions because the API endpoint region is not a billing filter.

## Boundaries

The MCP cannot mutate infrastructure or execute arbitrary CLI, SDK, SQL or shell.
Skills can guide authorized changes through appropriate existing tools, following
[the operator contract](docs/operations.md). MCP read-only annotations are hints;
IAM and the fixed tool implementation enforce the actual boundary.

The product map has 31 navigation units with explicit validation levels. It is not
an exhaustive Oracle commercial catalog. APEX/Fusion/multicloud application flows,
principal auth modes beyond API keys, production deployments, database migrations,
restores and all regional/price/support matrices have not been integration-tested.
The earlier proposed certification taxonomy is not included or claimed complete.

Original research clones, session artifacts and private tenancy evidence are
excluded from Git. No personal use cases, account IDs, credentials or customer data
are needed to install this package. Operational MCP results contain resource names
and IDs for follow-up reads and must remain private.
