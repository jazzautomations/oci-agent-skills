# Foundation mechanisms and reproducible checks

This guide describes HANDOFF-CODEX-2 on `v2-foundation`. Commands run from the
repository root. OCI verification is read-only; no tenancy mutation was executed.
Real skills, shared references, research, README and the root LICENSE belong to
other work packages. Their unresolved checks appear in CODEX-STATUS.md.

## Catalog and shared script libraries (W01/W03)

The pinned installed Click tree contains 9,145 leaves across 174 root groups.
The D3 wrapper allowlist has 3,601 leaves; the broader inventory `read` label has
3,708. The broader label includes verbs that D3 does not authorize. The wrapper
therefore cannot also satisfy the plan's contradictory “accept all 3,708” gate.
All these counts, the guard matrix, baseline findings and ownership counts come
from this command:

```bash
python3 scripts/foundation_report.py
```

`cli.jsonl` has one record per leaf; `cli-read.jsonl` is its strict read subset.
Every row carries the original scope disclaimer. `cli-meta.json` supplies global
option arity and import errors; `index.json` supplies root counts and purposes.
Required flags come from Click metadata and `[required]` help markers; callbacks
can impose additional requirements. Inventory does not establish authorization.

Generate and independently compare the pinned catalog, without credentials or
Click callbacks:

```bash
uv run --no-project --with oci-cli==3.91.0 python scripts/inventory.py --format jsonl --index
uv run --no-project --with oci-cli==3.91.0 python scripts/inventory.py --format jsonl --index --check
```

`catalog.py` supports find/help/required/severity/service/query, optional JSON,
and filtering by service, product text or a skill's example services. It limits
output to 400 UTF-8 bytes including the newline. JSON remains parseable and
marks truncation; misses exit 1 with suggestions. Skill queries describe example
coverage, not exhaustive skill ownership.

```bash
python3 scripts/catalog.py find "list instances" --read-only
python3 scripts/catalog.py required "compute instance list" --json
python3 scripts/catalog.py query --service compute --fields name,ops,read_only --json
python3 scripts/catalog.py query --skill oci-identity --json
uv run --frozen --project runtime pytest -q tests/test_catalog.py tests/test_console_url.py
```

`console_url.py` uses `https://cloud.oracle.com` only. Explicit region wins over
its shipped airport map, then the CLI environment/profile fallback; an absent
region produces a warning. Identity resources omit the region parameter.
Bucket names require a namespace, subnets require their VCN, and unmapped types
or noncommercial realms fail. Detail routes are explicitly unverified conventions.
The region map was derived from the supplied research/data/regions.json snapshot.

```bash
python3 scripts/console_url.py --ocid ocid1.instance.oc1.ord.example --json
```

`scripts/lib/oci_ro.sh` delegates to the importable Python wrapper. `check(argv)`
is pure; `run(argv)` returns `{ok,data|error,argv,truncated}`. Execution resolves
bounded, scalar `--from-json file://` options and rechecks them; the pure checker
and advisory hook ask/refuse unresolved file input. Nested opaque JSON is refused.
Known read leaves, local help/JSON-input generation and raw GET/HEAD are allowed.
The wrapper injects JSON output and a limit where supported, refuses debug and
interpretation-changing flags, and requires `OCI_RO_ALLOW_ALL=1` or the Python
`allow_all` argument for `--all`. Profile, auth, region and explicit endpoint
selection pass through. CLI defaults/aliases are disabled; argv is never evaluated.
The hook allows local `create-kubeconfig`, while the stricter wrapper refuses it.

Shell syntax is `oci_ro [--sanitize] [--trace] -- <oci argv>`. Cleaning is on by
default. `OCI_RO_TRACE=1` explicitly prints local argv to stderr. Exit codes are
0 success, 1 service/transport error, 2 internal error, 3 policy refusal. Service
stderr is replaced by a `{kind,status}` envelope. Internal `run_process` supports
help/validation consumers that keep raw output local.

```bash
bash scripts/lib/oci_ro.sh -- --help
uv run --frozen --project runtime pytest -q tests/test_oci_ro.py tests/test_guard.py -k wrapper
uv run --no-project --with oci-cli==3.91.0 python scripts/check_examples.py
```

The offline example checker validates all current fragment-derived examples
against installed Click definitions without invoking callbacks. The final skill
example population belongs to W42/W42a.

## Advisory guard and script provenance (W02)

`hooks/hooks.json` registers Bash PreToolUse only. Shell segments, prefixes,
pipelines, quotes and opaque forms are inspected without execution; the strongest
decision wins. Profile/auth selection is allowed, including operation-like values.
Hazardous flags require review. Denials exit 2; malformed input or a missing
redactor yields ask, empty context and exit 0. IAM is the security boundary.

| Inventory label | Allow | Ask | Deny |
| --- | ---: | ---: | ---: |
| read | 3,697 | 11 | 0 |
| mutating | 0 | 3,781 | 0 |
| destructive | 1 | 997 | 328 |
| unknown | 2 | 328 | 0 |

This is the **OCI leaf classifier only**, replayed over all 9,145 leaves. All 278
CRITICAL leaves are denied. `estimate-release-data-size` is the allowed census
false positive. The supplied purge regex denies `estimate-purge-data-size`, so
the plan's destructive 2/996/328 matrix cannot be reproduced with that same regex.
The measured 1/997/328 matrix is retained. Terraform, kubectl, SQL/APEX, sweep and
auto-approval rules are **unmeasured hand rules**, tested only as shell fixtures.

```bash
uv run --frozen --project runtime pytest -q -s tests/test_guard.py
```

`inventory.py --scripts` hashes each plugin Python/shell script into scripts.json
and binds that registry digest into guard.json. This is a reproducible digest,
not a cryptographic publisher signature. Unknown paths, changed hashes, registry
mismatch or hazardous argv ask for review. OCI-wrapper argv uses the same pure
check as execution. Other known scripts reject mutating/destructive argv tokens.
The guard policy source is scripts/guard_rules.json; catalog/guard.json is generated.

```bash
python3 scripts/inventory.py --scripts --examples --check
uv run --frozen --project runtime python scripts/ci/check_scripts_readonly.py
```

The static validator inspects executable Python AST and shell tokens for direct
OCI calls, and requires skill scripts to use the wrapper. Utilities and CI
programs that never call OCI do not import it merely to satisfy a text search.
Static checks and hashes are defense in depth, not proof about arbitrary Python.

## Untrusted output, auth and MCP (W01/W06/W07)

The shared sanitizer strips control/format/private/surrogate codepoints, flags
bidi and collapsed newlines, truncates by codepoint using field budgets, and
adds advisory pattern flags. Original printable codepoints are preserved;
normalization is used only for matching. Suspicious values remain visible inside
JSON delimiters. No `sanitized: true` claim is emitted. Cleaning its result is
idempotent; repeated cleaning of returned text also preserves that text.
`scripts/lib/redact.py` removes secret-shaped diagnostic values; scripts/redact.py
is a compatibility import. Runtime wheels include the shared sanitizer source.

```bash
uv run --frozen --project runtime pytest -q tests/test_sanitize.py tests/test_oci_ro.py
```

The ten research/15 injection fixtures are flagged and returned. Benign Japanese
and ASCII names have no flags; astral-plane truncation is tested. These are offline
fixtures, not a claim that malicious data was planted in OCI.

**15 shipped tools (14 credentialed + oci_price_lookup, credential-free).**

| Tools | Fixed operation family |
| --- | --- |
| oci_whoami, oci_regions, oci_compartments | Identity and compartment metadata |
| oci_instances, oci_network_inventory, oci_buckets | Projected inventory |
| oci_resource_search | Fixed exact-compartment query |
| oci_limit_services, oci_limit_values | Limit services and configured values |
| oci_cost_summary | Bounded dates, explicit scope and grouping depth |
| oci_work_requests, oci_alarm_status, oci_audit_events | Bounded operational diagnostics |
| oci_metrics | Fixed CPU/memory MQL templates |
| oci_price_lookup | Fixed-origin public SKU API |

Results carry `{source,trust,complete}` and flags; old content/scope notes are
removed. Completeness is relative to the requested page/scope, never a tenancy-wide
inventory claim, and false for truncation. TextContent uses ASCII JSON escaping;
error messages are descriptive. Tool schemas carry read-only annotations.

Auth caching follows TTL and credential-file changes. A 401 invalidates auth and
retries the fixed read once. This does not renew an expired local token. SDK work
runs in worker threads; tests verify concurrent stdio calls and event-loop
responsiveness below 100 ms. Subtree authorization checks actual ancestor links,
not OCID text prefixes. Bounded tenancy discovery is filtered for subcompartment
subtrees. Cost depth controls grouping, not authorization. See the
[runtime guide](../runtime/README.md) for environment settings and scope limits.

```bash
uv run --frozen --project runtime oci-readonly-smoke
uv run --frozen --project runtime pytest -q tests/test_runtime.py tests/test_runtime_foundation.py tests/test_runtime_tools.py
OCI_CONFIG_PROFILE=DEFAULT uv run --frozen --project runtime oci-readonly-smoke --live --region us-chicago-1
```

The 2026-09-08 live run passed all 12 D7 checks. Instances, alarms, Audit, metric
data and work requests are explicitly shape-only in this smoke. Only API-key
auth was exercised live. Other modes, realms, regions and detail branches remain
offline coverage. The schema is 13,820 characters, estimated at 3,455 tokens
(characters / 4, rounded up). This is not a tokenizer measurement.
The final plan's resident target is ≈6.3–6.5k tokens (≈3,020 descriptions + ≈3,300–3,500 MCP schemas, estimates);
final skill descriptions are not yet shipped, so that is not a measured release total.

## Template, CI and installed-host evidence (W05)

The template is the plan §4.1 stencil with only B3's canonical corpus path and
N3's `partial` enum applied. It deliberately contains placeholders and invalid
example YAML; content validators and installation exclude `_TEMPLATE`.

```bash
python3 scripts/ci/check_template.py
```

That byte comparison requires the coordinator's local research/00-PLAN-V2.1.md;
it is not a CI dependency. Frontmatter requires descriptions of at most 400
characters, literal `Use when:` and `Not for:`, and verified status
`live | partial | shape-only`. The six oracle-* names are pinned. Portable
validation strips to the six supported keys and validates the YAML projection.
References must resolve, appear in Route load-when rows, stay depth one, and have
a ToC above 100 lines; non-Markdown corpus files are exempt from naming rules.
Fences require real leaves, required flags, bounded lists, and mutation/rollback
markers. The live-help mode constructs fresh help argv; it never runs a mutation.

```bash
uv run --frozen --project runtime python scripts/ci/check_frontmatter.py
uv run --frozen --project runtime python scripts/ci/check_portable.py
uv run --frozen --project runtime python scripts/ci/check_refs.py
uv run --frozen --project runtime python scripts/ci/lint_fences.py skills docs README.md --live-help
uv run --frozen --project runtime python scripts/ci/check_budget.py
uv run --frozen --project runtime python scripts/ci/check_licenses.py
uv run --frozen --project runtime python scripts/ci/check_no_secrets.py
python3 scripts/ci/check_history.py
uv run --frozen --project runtime pytest -q tests/test_validators.py
```

Strict content validators expose protected legacy debt. The baseline is explicit:
append `--baseline catalog/validation-baseline.json` to frontmatter, portable,
refs, budget and license commands to reproduce the CI comparison. New **and stale**
findings fail. Refresh only after reviewing content-owner changes:

```bash
uv run --frozen --project runtime python scripts/ci/update_baseline.py
```

The root LICENSE is MIT and current skills lack LICENSE.txt. Planned Apache-2.0
manifest metadata does not relicense that material; publication needs the owner's
license correction. Budget figures are estimates. The secret checker scans
tracked source; the companion history checker prints only match counts. Both
are heuristic scans, not proof that arbitrary sensitive material is absent.

```bash
python3 scripts/ci/probe_paths.py
```

`scripts/ci/paths-probe.json` records Claude Code 2.1.263 against a loopback mock
API, using an isolated plugin, matching/nonmatching reads and a no-paths control.
There are no model or OCI calls. Descriptions are available before and after both
reads, so paths does **not gate description availability** in this host. No added
body activation was observed. The six planned keys can remain under N2's no-gating
condition; this result does not establish behavior in other hosts or versions.

Nightly documentation checks and Tuesday CLI drift are separate workflows:

```bash
python3 scripts/ci/check_links.py --offline
python3 scripts/ci/check_links.py references
uv run --no-project --with oci-cli==3.91.0 python scripts/ci/cli_drift.py
```

The link checker requires 200 for positive URLs and 404 for the known research/13
negative fixtures. The 2026-09-08 reference run passed 23 positive URLs and five
negative fixtures; scripts/ci/link-check-report.json records the response codes.
It is not a PR network gate. CLI drift compares
`path<TAB>sorted required flags`, checks newer upstream `[BREAKING]` paragraphs
for shipped command prefixes, retains a diff artifact and opens an issue on
change. The changelog parser is `python3 scripts/ci/cli_breaking.py <CHANGELOG.rst>`
(default baseline 3.91.0). Those hosted schedules have not been executed from this local handoff.

## Packaging, ownership and final regeneration (W08a/W42a)

The Claude manifest and all three marketplace entries carry hooks; marketplace
entries have no skills arrays yet. W08b supplies final subsets. Codex uses its
inline MCP launcher and root-relative cwd. The installer refuses unguarded hosts
without `--i-accept-unguarded`, preserves existing targets, and copies shared
references with rewritten paths. Source skills/references are unchanged.

```bash
python3 scripts/ci/check_manifests.py --host-validation
uv run --frozen --project runtime pytest -q tests/test_installer.py tests/test_packaging.py
bash installers/install.sh --target /tmp/oci-foundation-install --host claude --copy-shared
find /tmp/oci-foundation-install -type l
```

The copied plugin and marketplace pass installed Claude strict validation. Host
launchers pass stdio discovery from unrelated working directories and paths with
spaces, using bogus credential files. Interactive pickup in every host UI is not
claimed. The copy contains no symlinks before `uv` creates an environment. Literal
`find . -type l` in this source checkout remains nonempty because private research
and the runtime environment contain existing links. They are not distributed.
Root/bare-skills strict validation sees the required placeholder stencil; W08b
must validate the distribution shape and final skill selection.

[Installation](install.md) documents each host and its guard status.
[Optional MCP](mcp-optional.md) keeps Oracle oci-api on demand with a generic-executor
warning and skips oci-cloud because no verified read-only permission gate exists.

`foundation_report.py` separately reports the plan's 11 unowned content roots
(258 leaves), with counts from index.json: marketplace-publisher,
marketplace-private-offer, costad, demand-signal, mngdmac, cpg, dif, gdp, ccc, psa,
ddfs. The snapshot roots with no D3 leaf entries are a different set:
email-data-plane, logging-ingestion, model-deployment, raw-request, session, setup.
Raw GET/HEAD is allowed only when its method and target are supplied.

**W42a must run after W09–W41.** Skill authors write example fragments and scripts;
the coordinator then regenerates the registry, merged examples and guard binding:

```bash
python3 scripts/inventory.py --scripts --examples
python3 scripts/inventory.py --scripts --examples --check
uv run --no-project --with oci-cli==3.91.0 python scripts/check_examples.py
uv run --frozen --project runtime pytest -q tests
```

Until that regeneration, new skill scripts are unknown and require review. Final
reference provenance/tag retention, content budgets/licenses, W08b selection,
evaluations and publication remain with their named content/release packages.
