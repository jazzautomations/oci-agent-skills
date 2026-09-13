# Final validation matrix — 2026-09-13

Branch: `main`. **Not release-ready: 24 PASS, four nonpassing gates.**

The [September 13 query follow-up](query-validation-2026-09-13.md) audits all 106
Luna command proposals and finds six field errors in this package. The original
40/40 fixture score does not certify those commands. New response-field CI checks
and fresh service/scheduler reads retain V24/V25/V27/V28 as open.
The [September 13 follow-up](validation-closeout-2026-09-13.md) rechecks service
prerequisites and the actual weekly schedule. Its standalone suite passes 589
tests; the installation/adapter suite passes 20. Cloud Guard remains disabled,
Support returns 403, and the selected settled cost window remains empty.
The subsequent [alternative-host record](alternative-host-validation-2026-09-13.md)
records Devin/OpenCode attempts and a separate Cloud Guard setup refusal.
The paragraphs below preserve the earlier development measurements and their dates.

The [service follow-up](service-prerequisites-2026-09-11.md) fixes an unconditional
FinOps regional-gap flag and reports missing billing evidence explicitly. Seven
fresh scoped reads retain Cloud Guard DISABLED, Support 403 and empty settled
costs; the full local suite passes 582 tests. This does not close V25.
Standard validation is read-only. Separately authorized disposable labs are documented
in the [first](live-validation-2026-09-11.md) and [second](second-validation-2026-09-11.md)
reports; both have been torn down. The owner-authorized [history cleanup](history-migration-2026-09-11.md)
is published and independently verified. The [hosted drift publication](evidence/hosted-drift-publication-2026-09-11.json)
created issue #1; the actual Tuesday scheduler trigger is still unobserved.

Additional [native-host evidence](native-validation-2026-09-11.md) establishes
installation/activation and the public-price MCP path, plus 80 restricted synthetic
task attempts. It does not close V27/V28. Support triage's corrected user context
and response projection were tested; the service still returns 403, retaining V25.

The earlier [task repairs](task-repair-validation-2026-09-11.md) changed five skill
bodies and the checker. A fresh paired regression recovered four of the five
previously failed native cases; the baseline passed three. The fifth retains an
exact-format failure. This is not a full 40-task measurement, so V27 is UNMEASURED
for current full-task behavior. Historical 35/40 and 29/40 reports still replay
with their original verifiers and retain their original grades.

The [offline follow-up](offline-followup-2026-09-11.md) clarifies T04's name-only
output contract. At that date, its behavior had not been remeasured: the five-case regression
became historical too, its FAIL was retained, and fresh inference was paused.

[Earlier offline checks](evidence/offline-followup-checks-2026-09-11.json) passed
**577 tests, three warnings, 104.74 seconds**, and the full CLI-help fence check.
The [raw matrix](evidence/offline-followup-release-gate-2026-09-11.json) retains
24 PASS, two PARTIAL, one FAIL and one UNMEASURED. Cloud/link evidence keeps its
original dates. The default gate replays host access evidence without inference;
`--probe-host` requires separate model-provider budget approval, not OCI credits.

Reproduce: `uv run --frozen --project runtime python scripts/ci/release_gate.py`,
with Python from the pinned OCI CLI installation supplied via `--cli-python`.
The command writes scratch evidence and exits nonzero while any gate is open.

| Gate | Command | Result | Date | Evidence / reason / owner |
|---|---|---|---|---|
| V1 | `claude plugin validate . --strict` | PASS | 2026-09-13 | Command passed. |
| V2 | `claude plugin validate ./skills --strict` | PASS | 2026-09-13 | Command passed. |
| V3 | `uv run --frozen --project runtime python scripts/ci/check_frontmatter.py` | PASS | 2026-09-13 | Command passed. |
| V4 | `uv run --frozen --project runtime python scripts/ci/check_portable.py` | PASS | 2026-09-13 | Command passed. |
| V5 | `uv run --frozen --project runtime python scripts/ci/check_refs.py` | PASS | 2026-09-13 | Command passed. |
| V6 | `uv run --frozen --project runtime python scripts/ci/lint_fences.py skills docs references README.md --live-help` | PASS | 2026-09-13 | Command passed. |
| V7 | `uv run --frozen --project runtime python scripts/ci/check_links.py` | PASS | 2026-09-13 | Recorded evidence from this handoff; see docs/evidence/validation-links.json. |
| V8 | `uv run --frozen --project runtime pytest -q tests/test_guard.py` | PASS | 2026-09-13 | Severity matrix: docs/evidence/guard-severity-matrix.json, measured against a sha-pinned snapshot derived from the same generator as the catalog. Independent check: zero allows outside the strict read-only set; after deny rules, classify_leaf returns ask whenever read_only is false. All 278 critical leaves denied. Non-OCI rules are unmeasured. |
| V9 | `uv run --frozen --project runtime pytest -q tests -k parse` | PASS | 2026-09-13 | Command passed. |
| V10 | `uv run --frozen --project runtime pytest -q tests -k plugin_script` | PASS | 2026-09-13 | Command passed. |
| V11 | `uv run --frozen --project runtime python scripts/ci/check_scripts_readonly.py` | PASS | 2026-09-13 | Command passed. |
| V12 | `uv run --frozen --project runtime pytest -q tests -k 'redact or sanitize'` | PASS | 2026-09-13 | Command passed. |
| V13 | `uv run --frozen --project runtime oci-readonly-smoke` | PASS | 2026-09-13 | Command passed. |
| V14 | `UV_LINK_MODE=symlink uv run --frozen --project runtime pytest -q tests skills/oci-incident-triage/tests skills/oci-security-posture/tests skills/oci-sdk-patterns/tests --tb=short` | PASS | 2026-09-13 | Standalone rerun: 589 passed, 3 warnings in 61.85s. Combined-run failures retained separately; see docs/evidence/validation-closeout-2026-09-13.json. |
| V15 | `UV_LINK_MODE=symlink uv run --frozen --project runtime pytest -q tests/test_packaging.py tests/test_installer.py -x --tb=short` | PASS | 2026-09-13 | Standalone rerun: 20 passed, 1 warning in 70.76s. Fresh copied source is checked before runtime dependency setup; see docs/evidence/validation-closeout-2026-09-13.json. |
| V16 | `uv run --frozen --project runtime pytest -q tests/test_catalog.py; CLI_PYTHON scripts/inventory.py --format jsonl --index --check; CLI_PYTHON scripts/generate_read_contracts.py --check` | PASS | 2026-09-13 | Command passed. Subcheck V16-regeneration: PASS. Subcheck V16-read-contracts: PASS. |
| V17 | `uv run --frozen --project runtime pytest -q tests/test_console_url.py` | PASS | 2026-09-13 | Command passed. |
| V18 | `CLI_PYTHON scripts/check_examples.py --report docs/evidence/validation-examples-offline.json` | PASS | 2026-09-13 | Command passed. |
| V19 | `uv run --frozen --project runtime python scripts/eval/run.py --json evals/results/offline.json` | PASS | 2026-09-13 | Recorded semantic selection, worst trial 100.0%; required ≥90%; overlap pairs 4/4. Input-bound evidence, no fresh CI inference or host task execution. |
| V20 | `uv run --frozen --project runtime python evals/run_routing.py --negatives` | PASS | 2026-09-13 | Zero negative firings in every recorded semantic trial; input hashes and predictions are checked offline. |
| V21 | `uv run --frozen --project runtime python scripts/ci/check_budget.py` | PASS | 2026-09-13 | Command passed. |
| V22 | `uv run --frozen --project runtime python scripts/ci/check_no_secrets.py; uv run --frozen --project runtime python scripts/ci/check_history.py` | PASS | 2026-09-13 | Command passed. Subcheck V22-history: PASS. |
| V23 | `uv run --frozen --project runtime python scripts/ci/check_licenses.py` | PASS | 2026-09-13 | Command passed. |
| V24 | `CLI_PYTHON scripts/ci/cli_drift.py; .github/workflows/cli-drift.yml; CLI_PYTHON scripts/ci/cli_drift.py` | PARTIAL | 2026-09-11 | Hosted publication run 34632699299 passed and created issue #1. Manual preview and mocked duplicate-handling tests remain recorded. The actual Tuesday scheduled trigger is not yet observed. See docs/evidence/hosted-drift-publication-2026-09-11.json. Owner: repository CI maintainers. |
| V25 | `CLI_PYTHON scripts/check_examples.py --live --profile DEFAULT --region us-chicago-1 --report docs/evidence/validation-cli.json` | FAIL | 2026-09-11 | 36 CLI reads passed; 232 syntax-only examples. Paid-lab sweep: 38 passed, two triage failures (Cloud Guard 404/Support 403), two FinOps coverage gaps, four inert SQL files. See docs/live-validation-2026-09-11.md. Current offline recheck: docs/evidence/second-lab-release-gate-2026-09-11.json; retained live evidence, not a new fixture deployment. The second separate setup attempt returned Cloud Guard HTTP 500 after policy propagation; the temporary policy was removed and disabled state independently confirmed. Owner: OCI operator / skill maintainers. |
| V26 | `OCI_CONFIG_PROFILE=DEFAULT OCI_CLI_PROFILE=DEFAULT uv run --frozen --project runtime oci-readonly-smoke --live --region us-chicago-1` | PASS | 2026-09-11 | Recorded evidence from this handoff; see docs/evidence/validation-mcp.json. |
| V27 | `Recorded evals/results/host.json (no inference); uv run --frozen --project runtime python scripts/eval/verify_native_reference_benchmark.py evals/results/native-reference-benchmark-2026-09-11.json; CLI_PYTHON scripts/eval/verify_native_command_audit.py evals/results/native-reference-benchmark-2026-09-11.json evals/results/native-reference-command-audit-2026-09-11.json; uv run --frozen --project runtime python scripts/eval/verify_checked_task_benchmark.py evals/results/checked-task-benchmark-2026-09-11.json; CLI_PYTHON scripts/eval/verify_native_command_audit.py evals/results/checked-task-benchmark-2026-09-11.json evals/results/checked-task-command-audit-2026-09-11.json; uv run --frozen --project runtime python scripts/eval/task_repair_regression.py --report evals/results/task-repair-regression-2026-09-11.json` | UNMEASURED | 2026-09-11 | Skills and checker changed after the 35/40 measurement. The full report and five-case regression retain their historical scores, not current behavioral certification. New inference is paused; the default gate replays evidence only. See docs/offline-followup-2026-09-11.md. Subcheck V27-reference: PASS. Subcheck V27-syntax: PASS. Subcheck V27-checked: PASS. Subcheck V27-checked-syntax: PASS. Subcheck V27-repair: PASS. Owner: evaluation maintainers. |
| V28 | `uv run --frozen --project runtime python scripts/eval/head_to_head.py; uv run --frozen --project runtime python scripts/eval/head_to_head.py; uv run --frozen --project runtime python scripts/eval/verify_tool_task_benchmark.py evals/results/tool-task-benchmark-structured-2026-09-11.json` | PARTIAL | 2026-09-11 | Four offline arms and a separate controlled model-backed synthetic MCP measurement are recorded. See docs/tool-task-benchmark.md for 160 attempts, grades, costs and limitations. Original native four-product deployment comparison remains unmeasured. Subcheck V28-offline: PASS. Subcheck V28-fixtures: PASS. Owner: evaluation maintainers. |

PASS refers only to the stated scope. V19/V20 verify dated semantic-classification
evidence, not fresh model execution. V24 has real hosted notification evidence,
but no actual Tuesday scheduler observation. V25/V26 establish selected bounded reads, not complete workloads or
inventories. The [four-arm fixture-tool benchmark](tool-task-benchmark.md) includes
actual model tool calls, but does not instantiate the native products required by
V27/V28. The distributed tree is inspected before runtime-created environment links.
