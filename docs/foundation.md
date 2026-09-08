# Foundation mechanisms and reproducible checks

This document describes the foundation shipped by W01, W02, W04, W05, W06 and the
installer. Existing skill content and older product documentation are maintained by
the content work packages. All commands below run from the repository root unless
an installed path is explicitly specified. No verification command mutates an OCI tenancy.

## Catalog and script execution

`catalog/cli.jsonl` contains one installed CLI leaf per line, including aliases,
required flags, help text, capability flags and heuristic severity. The strict script
allowlist is `catalog/cli-read.jsonl`. `catalog/index.json` summarizes each CLI root;
`catalog/cli-meta.json` carries the original inventory scope disclaimer, global option
arity and import errors for both JSONL files. The inventory disclaimer concerns what
Click definitions establish; heuristic labels do not establish authorization.

Reproduce the CLI version, all catalog counts, guard matrix and legacy finding counts:

```bash
python3 scripts/foundation_report.py
```

The snapshot contains 9,145 leaves across 174 CLI roots. The script allowlist contains
3,601 leaves. The census's broader `read` label contains 3,708 leaves and includes
operations outside the script policy. These counts come from the report command above.
The installed loader and the research census differ in some alias spellings; replay
uses the shipped installed-CLI snapshot rather than a private research dependency.

Regenerate or compare in an environment containing the pinned OCI CLI:

```bash
uv run --no-project --with oci-cli==3.91.0 python scripts/inventory.py --format jsonl --index --check
# Remove --check to replace the generated catalog artifacts.
```

CI installs the same pinned CLI and executes this generator directly. `--check`
regenerates in a temporary directory and compares every generated file byte for byte.
No credentials or service calls are involved. Required flags are best-effort Click
metadata: callbacks can impose additional requirements.

Query helpers cap output at 400 UTF-8 bytes, a conservative token bound. A capped
answer is marked; use installed CLI help for the complete parameter list.

```bash
python3 scripts/catalog.py find "list instances" --read-only
python3 scripts/catalog.py help "compute instance list"
python3 scripts/catalog.py severity "compute instance terminate"
python3 scripts/catalog.py service compute
uv run --frozen --project runtime pytest -q tests/test_catalog.py
```

Plugin scripts execute OCI through `scripts/lib/oci_ro.py`; `oci_ro.sh` delegates to
that same implementation. Only known read leaves and local help/JSON-input generation
are accepted. The policy admits the specified list/get/search/head/summarize/describe
verb families and the explicit exceptional paths in `scripts/catalog_rules.py`.
Unknown leaves, opaque JSON input, interactive modes and interpretation-changing
options are refused with exit 3 and a fixed one-line reason. Arguments are passed as
an array, never evaluated as shell text; CLI aliases/default files are disabled.

```bash
bash scripts/lib/oci_ro.sh compute instance list --help
uv run --frozen --project runtime pytest -q tests/test_guard.py -k wrapper
```

## Advisory Bash guard

`hooks/hooks.json` registers only a Bash `PreToolUse` hook. The hook parses shell
segments, inspects OCI invocations under prefixes and pipelines, and recognizes plugin
script paths. It returns `allow`, `ask` or `deny`; denial exits 2. Malformed input,
opaque evaluation and redactor/import failures require review without echoing payloads.
Opaque `--from-json` inputs require review; the guard never reads their files.
The strongest identified segment decision wins. The hook is advisory defense in depth;
IAM is the actual access boundary.

Profile and auth selection do not by themselves require approval. Force/bulk/empty-bucket
hazards require review. Terraform apply/destroy/state removal, auto-approval, kubectl
mutation and SQL/APEX removal patterns are **unmeasured hand rules**. Shell fixtures
exercise these rules but are not a statistical classification evaluation.

The following is the measured **OCI leaf classifier only**. It does not measure arbitrary
shell behavior, IAM enforcement, argument values, or a live command execution:

| Census label | Allow | Ask | Deny |
| --- | ---: | ---: | ---: |
| read | 3,697 | 11 | 0 |
| mutating | 0 | 3,781 | 0 |
| destructive | 1 | 997 | 328 |
| unknown | 2 | 328 | 0 |

All 278 CRITICAL-labeled leaves are denied. `estimate-release-data-size` is the single
allowed destructive-labeled leaf: the census label is a known false positive.
`estimate-purge-data-size` remains denied by the purge rule. This measured result is
intentionally reported instead of copying the research's inconsistent allow/deny totals.

```bash
uv run --frozen --project runtime pytest -q -s tests/test_guard.py
python3 scripts/foundation_report.py
```

The test suite replays every catalog leaf, compares the result to `catalog/guard.json`,
and includes 60 explicit shell forms and 20 opaque/bypass-form fixtures plus regression
cases. Fixture payloads are only parsed; they are never executed. The redactor handles
OCIDs, bearer tokens, private-key blocks, password/token assignments and PAR paths.

## Skill template and CI

`skills/_TEMPLATE/SKILL.md` defines Scope check, Route, Commands, Failure modes and
Hard rules. Metadata validation requires matching names and descriptions of at most
400 characters containing `Use when` and `Not for`. Reference validation resolves local
links and forbids cross-doc skill links. Fence validation checks known leaves, required
parameters and explicit list bounds; help-only examples do not require runtime parameters.

```bash
uv run --frozen --project runtime python scripts/ci/check_frontmatter.py
uv run --frozen --project runtime python scripts/ci/check_refs.py
uv run --frozen --project runtime python scripts/ci/lint_fences.py --live-help
uv run --frozen --project runtime python scripts/ci/check_no_secrets.py
```

The first two strict commands currently fail on pre-existing content: 16 description
routing findings and 25 prohibited cross-doc links. The exact findings are recorded in
`catalog/validation-baseline.json`. No existing skill was rewritten. All fenced commands
pass the installed help check. These statements are reproduced by the commands above;
`foundation_report.py` also reports the baseline counts.

CI uses the following explicit baseline comparison. New findings **and removed/stale
exemptions** fail, so content fixes must also remove their baseline entries:

```bash
uv run --frozen --project runtime python scripts/ci/check_frontmatter.py --baseline catalog/validation-baseline.json
uv run --frozen --project runtime python scripts/ci/check_refs.py --baseline catalog/validation-baseline.json
uv run --frozen --project runtime pytest -q tests/test_validators.py
```

The live-help validator constructs fresh leaf-plus-help arguments; it never executes a
fenced example's operational arguments. The secret scan checks tracked files, rejects
credential-shaped material and rejects tracked symlinks. Generated virtual environments
and private research are not distribution payloads.

## Runtime scope, auth and diagnostics

The MCP surface contains fourteen annotated read-only tools. `oci_limits` combines
service discovery and value lookup, allowing all six requested additions without
advertising fifteen tools. The separate legacy limit tool names are no longer exposed.

| Tool | Contract |
| --- | --- |
| `oci_whoami` | Effective identity/configuration, tenancy name and region subscriptions; no keys |
| `oci_regions` | Authenticated tenancy region subscriptions |
| `oci_compartments` | Child compartment metadata, optional permitted subtree |
| `oci_instances` | Projected compute inventory |
| `oci_network_inventory` | VCN, subnet or NSG metadata |
| `oci_buckets` | Bucket metadata; no object bodies |
| `oci_resource_search` | Fixed exact-compartment query |
| `oci_limits` | Services, or configured values when `service_name` is supplied |
| `oci_cost_summary` | Bounded dates, explicit descendant/region scope and depth |
| `oci_work_requests` | Common work-request inventory or scoped status/errors/logs |
| `oci_alarm_status` | Alarm status, or scoped history with a bounded time window |
| `oci_audit_events` | Event/principal/resource/status projection; no request payloads |
| `oci_metrics` | Fixed CPU/memory templates; bounded time and datapoints |
| `oci_price_lookup` | Credential-free public SKU lookup with fixed origin and no redirects |

The following commands verify the surface, scope checks, token expiry, credential-file
changes, retry limits, concurrent `tools/call` over stdio, field projections and bounds:

```bash
uv run --frozen --project runtime oci-readonly-smoke
uv run --frozen --project runtime pytest -q tests/test_runtime.py tests/test_runtime_foundation.py tests/test_runtime_tools.py
```

Auth contexts expire by TTL or credential-file changes. HTTP 401 invalidates auth and
retries the fixed read once. This does not renew an expired local session token.
Blocking SDK calls execute in worker threads. Descendant permissions follow verified
parent relationships, not OCID string prefixes. Subcompartment subtree reads filter
bounded tenancy-level discovery because OCI restricts its native subtree flag to
the tenancy root. Configure `OCI_ALLOWED_COMPARTMENT_IDS`,
`OCI_ALLOWED_COMPARTMENT_MODE=exact` or `OCI_ALLOWED_COMPARTMENT_SUBTREES` as described in
[the runtime guide](../runtime/README.md). Failed ancestry lookups do not widen scope.

Costs declare excluded scopes. `include_descendants` constructs an explicit compartment
filter after bounded discovery; `compartment_depth` only controls grouping. IAM visibility
can omit compartments and costs. `all_regions` removes the region filter. A truncated
response is never a complete inventory or total. Audit has no server-side limit; an
oversized page is capped without a cursor. Common work requests do not cover every
service-specific work-request API. Empty metrics do not establish zero utilization.

Names are untrusted account data. They are bounded and stripped of control characters;
work-request messages are redacted. Public pricing supports Oracle's documented `prices`
field and observed `currencyCodeLocalizations` field; an absent SKU yields no prices.
The source API is described in [Oracle's cost-estimation documentation](https://docs.oracle.com/en-us/iaas/Content/Billing/Tasks/signingup_topic-Estimating_Costs.htm).

For authorized live reads, set the desired region and profile:

```bash
OCI_CONFIG_PROFILE=DEFAULT uv run --frozen --project runtime oci-readonly-smoke --live --region "$OCI_REGION"
```

The completed foundation run passed all 18 smoke checks against DEFAULT in us-chicago-1.
To reproduce that exact selection, replace `"$OCI_REGION"` with `us-chicago-1` above.
The output contains only counts and sanitized statuses. It measures API-key authentication;
other auth modes and resource-specific detail/history branches have offline coverage,
not a claim of live coverage. Live results can change with tenancy state and IAM.

Schema token counts emitted by smoke are **estimates**: compact schema characters divided
by four, rounded up. Use the reported character count to reproduce the estimate; no exact
tokenizer count is claimed. The current surface is below the planned 3,500-token estimate.

## Copy-only installation

Install into a new or empty directory outside the source repository:

```bash
bash installers/install.sh --target /tmp/oci-foundation-install
# Optional: --host codex|gemini|cursor|opencode (default: all)
uv run --frozen --project runtime pytest -q tests/test_installer.py tests/test_packaging.py
```

The installer copies plugin files, copies shared root `references/` when present, and
creates ordinary host skill files with relocated Markdown links. It excludes private
research, credentials and build caches. It rejects symlinks and existing nonempty targets.
Publication uses a temporary sibling directory followed by a directory rename. No global
host settings are changed. The source root's canonical skill files remain intact.

Generated project settings follow the official host schemas:

- [Codex](https://developers.openai.com/codex/mcp/): `.codex/config.toml`, skills in `.agents/skills`.
- [Gemini CLI](https://geminicli.com/docs/tools/mcp-server/): `.gemini/settings.json`.
- [Cursor](https://prod.cursor.com/docs/mcp): `.cursor/mcp.json`.
- [OpenCode v2](https://opencode.ai/v2/docs/mcp-servers): `opencode.json` under `mcp.servers`; this is not the v1 nesting.

The tests launch each generated MCP command from an unrelated working directory and a
path containing spaces, with a nonexistent credentials file. This verifies stdio discovery
and annotations; it does not claim interactive pickup in every host UI. Absolute runtime
paths bind generated configurations to the chosen target. Reinstall after relocating it.

## Roots with no script read allowlist entries

Here, “unowned” means zero entries in this script allowlist, not lack of Oracle API support
or absence of a content skill. Reproduce the list directly from `catalog/index.json`:

```bash
python3 scripts/foundation_report.py --unowned-services
```

- `email-data-plane`
- `logging-ingestion`
- `model-deployment`
- `raw-request`
- `session`
- `setup`

Run the complete offline regression suite with the required command:

```bash
uv run --frozen --project runtime pytest -q tests
```

## Handoff 2: CI and `paths` evidence

Run the installed-host probe with `python3 scripts/ci/probe_paths.py`. It uses an
isolated temporary plugin, a loopback mock Anthropic API, and Read/Skill tools;
no model inference or OCI request occurs. The recorded output is
`scripts/ci/paths-probe.json`. On Claude Code 2.1.263, the skill description is
available both before and after reading `match.tf`, after reading `other.txt`,
and in the control without `paths`. Thus `paths` does **not gate description
availability** in this installed plugin host. No automatic body loading was
observed; this is not evidence that paths add activation. The six planned keys
can remain under N2's no-gating condition; real skill content was not edited.

The new strict validators are `check_portable.py`, `check_budget.py`,
`check_scripts_readonly.py`, `check_licenses.py`, and `check_links.py`, all under
`scripts/ci/`. Invoke each with `uv run --frozen --project runtime python`.
Links run nightly; `--offline` lists their inputs without requests. The known
negative URL fixtures come from research/13 and are checked for HTTP 404.
Budgets use characters / 4 rounded up, explicitly an estimate. Frontmatter now
requires the colons in `Use when:` / `Not for:` and the verified enum
`live | partial | shape-only`. The portable validator removes all keys outside
the six-key profile, round-trips YAML, then applies the same metadata validator.

Strict validators report protected legacy-content debt. CI compares it with
`catalog/validation-baseline.json`; new or stale findings fail. Reproduce the
snapshot explicitly with `uv run --frozen --project runtime python
scripts/ci/update_baseline.py`; review the diff before committing, and never
regenerate the baseline automatically in CI. The root license is not Apache-2.0
and existing skills lack LICENSE.txt; these are outside the handoff's ownership.

`check_scripts_readonly.py` checks executable Python AST/shell tokens for direct
OCI calls and requires the wrapper in skill scripts. Pure utilities and CI
programs that never call OCI do not need a meaningless wrapper import. Static
checks and hashes are defense in depth, not a proof about arbitrary Python.
`python3 scripts/inventory.py --scripts --examples --check` verifies the registry
and fragment merge. `.github/workflows/cli-drift.yml` compares installed CLI
`path<TAB>sorted required flags` on Tuesdays, retains a diff artifact, and opens
an issue for drift. The renderer is `python3 scripts/ci/cli_drift.py` in an
OCI-CLI environment; it invokes no Click callbacks.
