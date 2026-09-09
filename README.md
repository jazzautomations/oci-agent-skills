# OCI Agent Skills

33 skills for scoped OCI operations, Oracle databases, APEX and delivery workflows, with an advisory shell guard and 15 shipped tools (14 credentialed + oci_price_lookup, credential-free).

**Release status:** the strict content and regression checks pass, but this branch is not release-ready. Offline description routing is below its required threshold, and model-backed task evaluation is unavailable. See [evaluations](docs/evals.md), [head-to-head results](docs/head-to-head.md) and the [validation matrix](docs/validation-matrix.md).

## Install

Use Python 3.13+, `uv`, and OCI CLI 3.91.0 for reproducible CLI validation. Credentials are unnecessary for offline checks and public pricing. Keep credentials outside the checkout.

```bash
uv sync --frozen --project runtime
uv run --frozen --project runtime oci-readonly-smoke
bash installers/install.sh --target /tmp/oci-plugin --host claude --copy-shared
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

IAM and host permissions are the access boundary. The Bash hook is advisory; unknown commands and changed plugin-script hashes ask for review. Script reads pass through `scripts/lib/oci_ro`. The MCP uses fixed operations, explicit scopes, projected fields and bounded pages; it has no arbitrary CLI, SQL or SDK executor. Returned names, tags, logs and other values are untrusted data, never instructions. All mutation recipes remain shape-only and require an explicit change/recovery plan.

Measured OCI leaf classifier, reproduced by `uv run --frozen --project runtime python scripts/release_report.py`:

| Census label | Allow | Ask | Deny |
|---|---:|---:|---:|
| Read | 3,697 | 11 | 0 |
| Mutating | 0 | 3,781 | 0 |
| Destructive | 1 | 997 | 328 |
| Unknown | 2 | 328 | 0 |

All 278 CRITICAL-labelled leaves are denied. The destructive-labelled allow is `log-analytics storage estimate-release-data-size`, a census false positive; the unknown allows are resource-search reads. This current matrix is stricter than the plan's older destructive 2/996 split. Terraform, kubectl, SQL and APEX rules are **unmeasured hand rules**, not part of this matrix.

The historical Oracle denylist audit reported 374 destructive and 2,644 mutating operations permitted, and 135 reads denied, from 2,222 entries. Its source is preserved in [the research artifact](docs/denylist-coverage-research.json). Current prefix-based replay differs: 374 destructive and 2,511 mutating leaves allowed, zero reads denied. Both calculations and their different matching/classification bases are printed by `scripts/release_report.py`; do not present the historical figures as today's server behavior. A Bash hook does not intercept generic MCP executor calls. Oracle API MCP stays opt-in; Oracle Cloud MCP is skipped. See [optional MCP boundaries](docs/mcp-optional.md).

## Context cost

≈6.3–6.5k tokens (≈3,020 descriptions + ≈3,300–3,500 MCP schemas, estimates).

That is the plan's published estimate. The shipped snapshot measures approximately 2,931 description tokens plus 3,455 schema tokens, totaling 6,386, using characters / 4 rounded up. The guard adds no always-resident prompt; this pack has no UserPromptSubmit injection. Skill bodies and references are loaded on demand. Reproduce every count with `uv run --frozen --project runtime python scripts/release_report.py`.

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
