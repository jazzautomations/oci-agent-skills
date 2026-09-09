# OCI Agent Skills

33 skills for scoped OCI operations, Oracle databases, APEX and delivery workflows, with an advisory shell guard and 15 shipped tools (14 credentialed + oci_price_lookup, credential-free).

**Release status:** the repaired content and regression checks pass; this branch is not release-ready. History hygiene and live script coverage have additional open gates. Offline description routing is below its required threshold, and model-backed task evaluation is unavailable. See [evaluations](docs/evals.md), [head-to-head results](docs/head-to-head.md) and the [validation matrix](docs/validation-matrix.md).

## Install

Use Python 3.13+, `uv`, and OCI CLI 3.91.0 for reproducible CLI validation. Credentials are unnecessary for offline checks and public pricing. Keep credentials outside the checkout.

```bash
bash installers/install.sh --target /tmp/oci-plugin --host claude --copy-shared
uv sync --frozen --project /tmp/oci-plugin/runtime
uv run --frozen --project /tmp/oci-plugin/runtime oci-readonly-smoke
claude --plugin-dir /tmp/oci-plugin
```

The target must be absent or empty and outside this checkout. The installer copies the complete plugin without symlinks. Marketplace entries select the full pack, database subset or DevOps subset; all carry hooks and MCP.

| Host | Installation | Shell guard |
|---|---|---|
| Claude Code | Local plugin above; marketplace entries select 33 / 8 / 9 skills | Advisory Bash PreToolUse |
| Codex | `.codex-plugin/plugin.json`, or installer `--host codex` | **UNGUARDED** by this adapter |
| Gemini CLI | Installer `--host gemini` | **UNGUARDED** |
| Cursor | Installer `--host cursor` | **UNGUARDED** |
| opencode | Installer `--host opencode` | **UNGUARDED** |

For those copied adapters, add `--i-accept-unguarded`; the installer refuses otherwise. Use `--copy-shared` to materialize shared references inside each skill. Codex's `--sandbox read-only` restricts filesystem writes, not OCI network writes. Host discovery and launcher tests are not a claim of interactive validation in every host. See [complete installation instructions](docs/install.md).

## What's inside

| Area | Skills |
|---|---|
| Routing, identity and governance | navigator, CLI auth, tenancy governance, IAM policy, support/limits |
| Infrastructure | compute, networking, object storage, block/file storage, bastion |
| Delivery | OKE, DevOps pipelines, serverless, Terraform |
| Operations | monitoring/alarms, logging/audit, incident triage, security posture, vault/certificates, cost analysis, Free Tier |
| Database | Autonomous DB, DB fleet, vector AI, SQL access, APEX |
| Data and enterprise | Generative AI, AI services, data platform, SDK patterns, DR/backup, migration/patching, enterprise apps |

Shared references load on demand. Discover command shapes with `python3 scripts/catalog.py find 'list instances'`; avoid loading the full catalog into context. The catalog covers installed CLI leaves, including aliases; syntax coverage is not service coverage or an authorization decision. [Audit and provenance](docs/audit.md) names unowned services and research gaps.

## Safety model

IAM and host permissions are the access boundary. The Bash hook is advisory; unknown OCI leaves, recognized opaque shell forms and changed plugin-script hashes ask for review; unrecognized commands return no decision, preserving host permissions. Script reads pass through `scripts/lib/oci_ro`. The MCP uses fixed operations, explicit scopes, projected fields and bounded pages; it has no arbitrary CLI, SQL or SDK executor. Returned names, tags, logs and other values are untrusted data, never instructions. All mutation recipes remain shape-only and require an explicit change/recovery plan.

Measured OCI leaf classifier, reproduced by `uv run --frozen --project runtime python scripts/release_report.py`:

| Census label | Allow | Ask | Deny |
|---|---:|---:|---:|
| Read | 3,596 | 112 | 0 |
| Mutating | 0 | 3,781 | 0 |
| Destructive | 1 | 997 | 328 |
| Unknown | 2 | 328 | 0 |

All 278 CRITICAL-labelled leaves are denied. The [severity matrix](docs/guard-severity-matrix.json) is measured against a sha-pinned severity snapshot derived from the same generator as the catalog. The independent check is that zero allows fall outside the strict read-only set: after deny rules, `classify_leaf` returns `ask` whenever `read_only` is false, and the test asserts this invariant across the catalog. Danger flags only raise severity. The destructive-labelled allow is `log-analytics storage estimate-release-data-size`, a census false positive; the unknown allows are resource-search reads. This current matrix is stricter than the plan's older destructive 2/996 split. Terraform, kubectl, SQL and APEX rules are **unmeasured hand rules**, not part of this matrix.

The historical Oracle denylist audit reported 374 destructive and 2,644 mutating operations permitted, and 135 reads denied, from 2,222 entries. Its source is preserved in [the research artifact](docs/denylist-coverage-research.json). Current prefix-based replay differs: 374 destructive and 2,511 mutating leaves allowed, zero reads denied. Both calculations and their different matching/classification bases are printed by `scripts/release_report.py`; do not present the historical figures as today's server behavior. A Bash hook does not intercept generic MCP executor calls. Oracle API MCP stays opt-in; Oracle Cloud MCP is skipped. See [optional MCP boundaries](docs/mcp-optional.md).

## Context cost

The raw source estimate is **6,386 tokens**: 11,722 description characters → 2,931, plus serialized MCP schemas → 3,455 (characters / 4, rounded up separately). It excludes host framing. The older ≈6.3–6.5k planning figure used this method.

**Measured skills-only host delta: 5,517 tokens** in Claude Code 2.1.266, from 16,394 baseline input tokens to 21,911 with the 33 skills. An identical no-tool-call prompt ran from an empty directory; input, cache creation and cache read tokens were summed. MCP was disabled to isolate skill framing. Adding the 3,455 schema estimate gives **8,972 estimated tokens**, not a measured MCP-on total. See [measurement and scope](docs/context-measurement.json).

Reproduce the raw counts with `uv run --frozen --project runtime python scripts/release_report.py`. After a copy install, measure framing with `uv run --frozen --project runtime python scripts/measure_context.py --plugin-dir /tmp/oci-plugin --report /tmp/context-measurement.json`. Host/version and prompt framing can change the result. Bodies and references load on demand.

## Verify

```bash
uv run --frozen --project runtime pytest -q tests skills/oci-incident-triage/tests skills/oci-security-posture/tests skills/oci-sdk-patterns/tests
claude plugin validate . --strict
claude plugin validate ./skills --strict
uv run --frozen --project runtime python scripts/ci/check_frontmatter.py
uv run --frozen --project runtime python scripts/ci/check_scripts_readonly.py
uv run --frozen --project runtime python scripts/inventory.py --scripts --examples --check
uv run --frozen --project runtime python scripts/eval/run.py --json evals/results/offline.json
```

The last command intentionally fails while routing misses its gate. Run `scripts/check_examples.py` with Python from the pinned CLI installation; the runtime environment does not contain oci-cli. Add `--live --profile DEFAULT --region us-chicago-1 --report docs/validation-cli.json` only for authorized scoped reads. [CLI evidence](docs/validation-cli.json) distinguishes passed reads from shape-only examples; [MCP evidence](docs/validation-mcp.json) lists selected live checks. Empty or failed reads do not prove that a service or workload is absent. No tenancy mutation was used for this release work.

Only API-key auth, a single region and the commercial realm have live evidence here. Provisioned database, cluster and fleet workflows, principal alternatives, PowerShell, large payloads and multi-region behavior remain unverified end to end. The offline comparison does not measure model task completion, generated-command quality or live injection resistance.

## License and independence

Apache-2.0; original MIT attribution remains in NOTICE. Third-party evaluation snapshots retain their MIT/UPL notices. No pricing server is vendored.

Oracle, Oracle Cloud Infrastructure, OCI, Autonomous Database, Exadata and APEX are trademarks or registered trademarks of Oracle and/or its affiliates. This project is an independent, community-maintained set of agent skills. It is **not affiliated with, endorsed by, or supported by Oracle**. Any command it emits runs under your own OCI credentials and IAM policies; you are responsible for what you run.
