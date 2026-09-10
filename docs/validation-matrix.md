# Final validation matrix — 2026-09-10

Branch: `main`. **Not release-ready.** No tenancy mutations.

Reproduce: `uv run --frozen --project runtime python scripts/ci/release_gate.py --live --links --live-help`. Writes scratch evidence outside the checkout and prints unified diffs against tracked reports. This repeats only scoped read operations and public documentation GETs; skill prerequisites may remain blocked. Omit these flags to reuse dated live/link evidence and use snapshot fence lint. CLI_PYTHON denotes Python from the pinned OCI CLI installation; pass --cli-python to select it explicitly. A nonzero exit is expected while any gate remains red or unmeasured.

| Gate | Command | Result | Date | Evidence / reason / owner |
|---|---|---|---|---|
| V1 | `claude plugin validate . --strict` | PASS | 2026-09-09 | Command passed. |
| V2 | `claude plugin validate ./skills --strict` | PASS | 2026-09-09 | Command passed. |
| V3 | `uv run --frozen --project runtime python scripts/ci/check_frontmatter.py` | PASS | 2026-09-09 | Command passed. |
| V4 | `uv run --frozen --project runtime python scripts/ci/check_portable.py` | PASS | 2026-09-09 | Command passed. |
| V5 | `uv run --frozen --project runtime python scripts/ci/check_refs.py` | PASS | 2026-09-09 | Command passed. |
| V6 | `uv run --frozen --project runtime python scripts/ci/lint_fences.py skills docs references README.md` | PASS | 2026-09-09 | Command passed. |
| V7 | `uv run --frozen --project runtime python scripts/ci/check_links.py` | PASS | 2026-09-09 | Recorded evidence from this handoff; see docs/evidence/validation-links.json. |
| V8 | `uv run --frozen --project runtime pytest -q tests/test_guard.py` | PASS | 2026-09-09 | Severity matrix: docs/evidence/guard-severity-matrix.json, measured against a sha-pinned snapshot derived from the same generator as the catalog. Independent check: zero allows outside the strict read-only set; after deny rules, classify_leaf returns ask whenever read_only is false. All 278 critical leaves denied. Non-OCI rules are unmeasured. |
| V9 | `uv run --frozen --project runtime pytest -q tests -k parse` | PASS | 2026-09-09 | Command passed. |
| V10 | `uv run --frozen --project runtime pytest -q tests -k plugin_script` | PASS | 2026-09-09 | Command passed. |
| V11 | `uv run --frozen --project runtime python scripts/ci/check_scripts_readonly.py` | PASS | 2026-09-09 | Command passed. |
| V12 | `uv run --frozen --project runtime pytest -q tests -k 'redact or sanitize'` | PASS | 2026-09-09 | Command passed. |
| V13 | `uv run --frozen --project runtime oci-readonly-smoke` | PASS | 2026-09-09 | Command passed. |
| V14 | `uv run --frozen --project runtime pytest -q tests skills/oci-incident-triage/tests skills/oci-security-posture/tests skills/oci-sdk-patterns/tests` | PASS | 2026-09-10 | 453 tests passed in the full suite including case-level semantic diagnostics. Temporary runtime dependencies used UV_LINK_MODE=symlink; distributed payload checks still require copies without symlinks. |
| V15 | `uv run --frozen --project runtime pytest -q tests/test_packaging.py tests/test_installer.py` | PASS | 2026-09-10 | Copy installation inspected: 37 skills, shared references, no authoring-only files or symlinks before runtime setup. |
| V16 | `uv run --frozen --project runtime pytest -q tests/test_catalog.py; CLI_PYTHON scripts/inventory.py --format jsonl --index --check` | PASS | 2026-09-09 | Command passed. Subcheck V16-regeneration: PASS. |
| V17 | `uv run --frozen --project runtime pytest -q tests/test_console_url.py` | PASS | 2026-09-09 | Command passed. |
| V18 | `CLI_PYTHON scripts/check_examples.py --report docs/evidence/validation-examples-offline.json` | PASS | 2026-09-09 | Command passed. |
| V19 | `uv run --frozen --project runtime python scripts/eval/run.py --json evals/results/offline.json` | PASS | 2026-09-10 | Recorded 37-skill semantic selection: 77/80 and 77/80, 4/4 overlap pairs in both trials. Current fingerprints verified; isolated description selection only. |
| V20 | `uv run --frozen --project runtime python evals/run_routing.py --negatives` | PASS | 2026-09-10 | Zero negative firings in both 40-case trials after the Classic comparison scope clarification; 15/15 synthetic boundaries pass. Previous failing catalog-expansion traces retained. Original corpus, labels, policy, model and seeds unchanged. |
| V21 | `uv run --frozen --project runtime python scripts/ci/check_budget.py` | PASS | 2026-09-09 | Command passed. |
| V22 | `uv run --frozen --project runtime python scripts/ci/check_no_secrets.py; uv run --frozen --project runtime python scripts/ci/check_history.py` | FAIL | 2026-09-09 | Command passed. Subcheck V22-history: FAIL. Owner: repository history owner. |
| V23 | `uv run --frozen --project runtime python scripts/ci/check_licenses.py` | PASS | 2026-09-09 | Command passed. |
| V24 | `CLI_PYTHON scripts/ci/cli_drift.py; .github/workflows/cli-drift.yml; CLI_PYTHON scripts/ci/cli_drift.py` | PARTIAL | 2026-09-10 | Hosted manual preview passed: run 34436615438, CLI 3.91.0 versus 3.92.1, captured diff and would-create notification without publication. Eight mock-client tests cover creation/deduplication. Actual Tuesday cron firing and real issue publication remain unmeasured. See docs/evidence/hosted-drift.json. Owner: repository CI maintainers. |
| V25 | `CLI_PYTHON scripts/check_examples.py --live --profile DEFAULT --region us-chicago-1 --report docs/evidence/validation-cli.json` | FAIL | 2026-09-10 | Script sweep: multipart namespace/bucket discovery repaired; 28 passed entrypoints, three missing resource prerequisites, two triage failures and two no-data metric checks. See docs/evidence/validation-scripts.json and release-readiness.md. Scope remains selected tenancy root and region. Owner: OCI operator / skill maintainers. |
| V26 | `OCI_CONFIG_PROFILE=DEFAULT OCI_CLI_PROFILE=DEFAULT uv run --frozen --project runtime oci-readonly-smoke --live --region us-chicago-1` | PASS | 2026-09-09 | Recorded evidence from this handoff; see docs/evidence/validation-mcp.json. |
| V27 | `claude plugin eval . --threshold 0.8 --json SCRATCH/run.json --output-dir SCRATCH --no-publish --no-scaffold --mocks record --max-cost-usd 1 --runs 1` | UNAVAILABLE | 2026-09-10 | Early-access restriction reproduced on 2026-09-10 for T01 with no tool grants, absent OCI config, mocks and no publication. No qualifying host task score. The accepted skill-creator task-evaluation alternative remains unmeasured; description triggering is insufficient. Owner: evaluation maintainers; native access: installed host provider. |
| V28 | `uv run --frozen --project runtime python scripts/eval/head_to_head.py; uv run --frozen --project runtime python scripts/eval/head_to_head.py` | PARTIAL | 2026-09-09 | All four offline arms complete, table and per-case retrieval deltas published. Original live/model-backed comparison and behavioral deltas unmeasured. Subcheck V28-offline: PASS. Owner: evaluation maintainers. |

PASS refers to the stated scope. V8 is the current measured OCI-leaf matrix; it does not measure non-OCI rules. V19/V20 verify dated semantic classification evidence and recompute its exact-match scores; CI does not make fresh model calls. The old lexical matcher is diagnostic only. V24 is not a hosted schedule run. V27 and the original behavioral V28 remain unmeasured. V25/V26 verify bounded selected reads, not deployed workloads or complete inventories. The distributed tree is checked before any uv-created environment symlinks.
