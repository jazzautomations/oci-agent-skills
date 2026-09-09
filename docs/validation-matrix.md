# Final validation matrix — 2026-09-09

Branch: v2-foundation. **Not release-ready.** No merge and no tenancy mutations.

Reproduce: `uv run --frozen --project runtime python scripts/ci/release_gate.py --live --links --live-help`. Writes scratch evidence outside the checkout and prints unified diffs against tracked reports. This repeats only scoped read operations and public documentation GETs; skill prerequisites may remain blocked. Omit these flags to reuse dated live/link evidence and use snapshot fence lint. CLI_PYTHON denotes Python from the pinned OCI CLI installation; pass --cli-python to select it explicitly. A nonzero exit is expected while any gate remains red or unmeasured.

| Gate | Command | Result | Date | Evidence / reason / owner |
|---|---|---|---|---|
| V1 | `claude plugin validate . --strict` | PASS | 2026-09-09 | Command passed. |
| V2 | `claude plugin validate ./skills --strict` | PASS | 2026-09-09 | Command passed. |
| V3 | `uv run --frozen --project runtime python scripts/ci/check_frontmatter.py` | PASS | 2026-09-09 | Command passed. |
| V4 | `uv run --frozen --project runtime python scripts/ci/check_portable.py` | PASS | 2026-09-09 | Command passed. |
| V5 | `uv run --frozen --project runtime python scripts/ci/check_refs.py` | PASS | 2026-09-09 | Command passed. |
| V6 | `uv run --frozen --project runtime python scripts/ci/lint_fences.py skills docs references README.md --live-help` | PASS | 2026-09-09 | Command passed. |
| V7 | `uv run --frozen --project runtime python scripts/ci/check_links.py` | PASS | 2026-09-09 | Recorded evidence from this handoff; see docs/validation-links.json. |
| V8 | `uv run --frozen --project runtime pytest -q tests/test_guard.py` | PASS | 2026-09-09 | Independent research-severity matrix: docs/guard-severity-matrix.json; 278 critical leaves denied, zero allows outside strict reads. Non-OCI rules are unmeasured. |
| V9 | `uv run --frozen --project runtime pytest -q tests -k parse` | PASS | 2026-09-09 | Command passed. |
| V10 | `uv run --frozen --project runtime pytest -q tests -k plugin_script` | PASS | 2026-09-09 | Command passed. |
| V11 | `uv run --frozen --project runtime python scripts/ci/check_scripts_readonly.py` | PASS | 2026-09-09 | Command passed. |
| V12 | `uv run --frozen --project runtime pytest -q tests -k 'redact or sanitize'` | PASS | 2026-09-09 | Command passed. |
| V13 | `uv run --frozen --project runtime oci-readonly-smoke` | PASS | 2026-09-09 | Command passed. |
| V14 | `uv run --frozen --project runtime pytest -q tests skills/oci-incident-triage/tests skills/oci-security-posture/tests skills/oci-sdk-patterns/tests` | PASS | 2026-09-09 | 260 passed, 1 warning in 52.39s |
| V15 | `uv run --frozen --project runtime pytest -q tests/test_packaging.py tests/test_installer.py` | PASS | 2026-09-09 | Command passed. Fresh copied tree: 33 skills, shared refs, hooks, MCP config and notices; find . -type l empty. |
| V16 | `uv run --frozen --project runtime pytest -q tests/test_catalog.py; CLI_PYTHON scripts/inventory.py --format jsonl --index --check` | PASS | 2026-09-09 | Command passed. Subcheck V16-regeneration: PASS. |
| V17 | `uv run --frozen --project runtime pytest -q tests/test_console_url.py` | PASS | 2026-09-09 | Command passed. |
| V18 | `CLI_PYTHON scripts/check_examples.py --report docs/validation-examples-offline.json` | PASS | 2026-09-09 | Command passed. |
| V19 | `uv run --frozen --project runtime python scripts/eval/run.py --json evals/results/offline.json` | FAIL | 2026-09-09 | Description proxy 37.5%; required ≥90%; overlap pairs 4/4. Not host routing. Owner: evaluation/routing maintainers. |
| V20 | `uv run --frozen --project runtime python evals/run_routing.py --negatives` | PASS | 2026-09-09 | Zero negative firings required; the matcher is a static proxy. |
| V21 | `uv run --frozen --project runtime python scripts/ci/check_budget.py` | PASS | 2026-09-09 | Command passed. |
| V22 | `uv run --frozen --project runtime python scripts/ci/check_no_secrets.py; uv run --frozen --project runtime python scripts/ci/check_history.py` | FAIL | 2026-09-09 | Command passed. Subcheck V22-history: FAIL. Owner: repository history owner. |
| V23 | `uv run --frozen --project runtime python scripts/ci/check_licenses.py` | PASS | 2026-09-09 | Command passed. |
| V24 | `CLI_PYTHON scripts/ci/cli_drift.py; .github/workflows/cli-drift.yml; CLI_PYTHON scripts/ci/cli_drift.py` | PARTIAL | 2026-09-09 | Local pinned required-flag renderer exercised; Tuesday schedule/hosted issue creation not executed locally. Subcheck V24-local: PASS. Owner: repository CI maintainers. |
| V25 | `CLI_PYTHON scripts/check_examples.py --live --profile DEFAULT --region us-chicago-1 --report docs/validation-cli.json` | FAIL | 2026-09-09 | Command passed. Skill entrypoint execution: FAIL; see docs/validation-scripts.json. Owner: OCI operator / skill maintainers. |
| V26 | `OCI_CONFIG_PROFILE=DEFAULT OCI_CLI_PROFILE=DEFAULT uv run --frozen --project runtime oci-readonly-smoke --live --region us-chicago-1` | PASS | 2026-09-09 | Recorded evidence from this handoff; see docs/validation-mcp.json. |
| V27 | `claude plugin eval . --threshold 0.8 --json SCRATCH/run.json --output-dir SCRATCH --no-publish --no-scaffold --mocks record --max-cost-usd 1 --runs 1` | UNAVAILABLE | 2026-09-09 | `plugin eval` is currently in early access See evals/results/host.json. No qualifying host task score. Owner: evaluation maintainers / installed host provider. |
| V28 | `uv run --frozen --project runtime python scripts/eval/head_to_head.py; uv run --frozen --project runtime python scripts/eval/head_to_head.py` | PARTIAL | 2026-09-09 | All four offline arms complete, table and per-case retrieval deltas published. Original live/model-backed comparison and behavioral deltas unmeasured. Subcheck V28-offline: PASS. Owner: evaluation maintainers. |

PASS refers to the stated scope. V8 is the current measured OCI-leaf matrix; it does not measure non-OCI rules. V19/V20 are deterministic description proxies. V24 is not a hosted schedule run. V27 and the original behavioral V28 remain unmeasured. V25/V26 verify bounded selected reads, not deployed workloads or complete inventories. The distributed tree is checked before any uv-created environment symlinks.
