# Final validation matrix — 2026-09-11

Branch: `main`. **Not release-ready: 24 PASS, four nonpassing gates.**
Standard validation is read-only. Separately authorized disposable labs are documented
in the [first](live-validation-2026-09-11.md) and [second](second-validation-2026-09-11.md)
reports; both have been torn down. The owner-authorized [history cleanup](history-migration-2026-09-11.md)
is published and independently verified. The [hosted drift publication](evidence/hosted-drift-publication-2026-09-11.json)
created issue #1; the actual Tuesday scheduler trigger is still unobserved.

Additional [native-host evidence](native-validation-2026-09-11.md) establishes
installation/activation and the public-price MCP path, plus 80 restricted synthetic
task attempts. It does not close V27/V28. Support triage's corrected user context
and response projection were tested; the service still returns 403, retaining V25.

The later [reference-enabled paired run](native-reference-validation-2026-09-11.md)
collected another 80 attempts. Common syntax-adjudicated scores are 29/40 native
and 13/40 baseline; that measurement remains below the 80% minimum.
The new opt-in [checked-command workflow](checked-task-validation-2026-09-11.md)
scored 35/40 native and 38/40 checker-enabled baseline. V27 is PARTIAL, not PASS:
this limited workflow meets the threshold, but full query/task semantics remain
unverified. The [latest full recheck](evidence/checked-task-release-gate-2026-09-11.json)
passed **544 tests with five warnings in 102.11 seconds** and retained the same
four nonpassing gates (24 PASS, three PARTIAL, one FAIL). It used snapshot fence
lint; [separately repeated live-help checks](evidence/checked-task-extra-checks-2026-09-11.json)
remain distinct from cloud execution.

Latest recheck: `uv run --frozen --project runtime python scripts/ci/release_gate.py`.
The pinned CLI Python was supplied explicitly. [Raw gate results](evidence/native-release-gate-2026-09-11.json)
record 496 passing tests; the [final full-suite rerun](evidence/native-final-regression-2026-09-11.json)
after the enum-conversion regression passed 497. [Extra strict checks](evidence/native-extra-checks-2026-09-11.json)
cover manifests, template, generated catalogs and both recorded task benchmarks.
The earlier [live-help recheck](evidence/second-lab-release-gate-2026-09-11.json)
remains the evidence for actual CLI help resolution; it was not repeated here.
Live reads and link checks retain their recorded dates. This recheck did not
provision fixtures or repeat all live calls. A nonzero exit is expected while any
gate remains red or unmeasured.

| Gate | Command | Result | Date | Evidence / reason / owner |
|---|---|---|---|---|
| V1 | `claude plugin validate . --strict` | PASS | 2026-09-11 | Command passed. |
| V2 | `claude plugin validate ./skills --strict` | PASS | 2026-09-11 | Command passed. |
| V3 | `uv run --frozen --project runtime python scripts/ci/check_frontmatter.py` | PASS | 2026-09-11 | Command passed. |
| V4 | `uv run --frozen --project runtime python scripts/ci/check_portable.py` | PASS | 2026-09-11 | Command passed. |
| V5 | `uv run --frozen --project runtime python scripts/ci/check_refs.py` | PASS | 2026-09-11 | Command passed. |
| V6 | `uv run --frozen --project runtime python scripts/ci/lint_fences.py skills docs references README.md` | PASS | 2026-09-11 | Command passed. |
| V7 | `uv run --frozen --project runtime python scripts/ci/check_links.py` | PASS | 2026-09-09 | Recorded evidence from this handoff; see docs/evidence/validation-links.json. |
| V8 | `uv run --frozen --project runtime pytest -q tests/test_guard.py` | PASS | 2026-09-11 | Severity matrix: docs/evidence/guard-severity-matrix.json, measured against a sha-pinned snapshot derived from the same generator as the catalog. Independent check: zero allows outside the strict read-only set; after deny rules, classify_leaf returns ask whenever read_only is false. All 278 critical leaves denied. Non-OCI rules are unmeasured. |
| V9 | `uv run --frozen --project runtime pytest -q tests -k parse` | PASS | 2026-09-11 | Command passed. |
| V10 | `uv run --frozen --project runtime pytest -q tests -k plugin_script` | PASS | 2026-09-11 | Command passed. |
| V11 | `uv run --frozen --project runtime python scripts/ci/check_scripts_readonly.py` | PASS | 2026-09-11 | Command passed. |
| V12 | `uv run --frozen --project runtime pytest -q tests -k 'redact or sanitize'` | PASS | 2026-09-11 | Command passed. |
| V13 | `uv run --frozen --project runtime oci-readonly-smoke` | PASS | 2026-09-11 | Command passed. |
| V14 | `uv run --frozen --project runtime pytest -q tests skills/oci-incident-triage/tests skills/oci-security-posture/tests skills/oci-sdk-patterns/tests` | PASS | 2026-09-11 | 544 passed, 5 warnings in 102.11s (0:01:42) |
| V15 | `uv run --frozen --project runtime pytest -q tests/test_packaging.py tests/test_installer.py` | PASS | 2026-09-11 | Command passed. Fresh copied tree: all source skills, shared refs, hooks, MCP config and notices; find . -type l empty. |
| V16 | `uv run --frozen --project runtime pytest -q tests/test_catalog.py; CLI_PYTHON scripts/inventory.py --format jsonl --index --check; CLI_PYTHON scripts/generate_read_contracts.py --check` | PASS | 2026-09-11 | Command passed. Subcheck V16-regeneration: PASS. Subcheck V16-read-contracts: PASS. |
| V17 | `uv run --frozen --project runtime pytest -q tests/test_console_url.py` | PASS | 2026-09-11 | Command passed. |
| V18 | `CLI_PYTHON scripts/check_examples.py --report docs/evidence/validation-examples-offline.json` | PASS | 2026-09-11 | Command passed. |
| V19 | `uv run --frozen --project runtime python scripts/eval/run.py --json evals/results/offline.json` | PASS | 2026-09-11 | Recorded semantic selection, worst trial 100.0%; required ≥90%; overlap pairs 4/4. Input-bound evidence, no fresh CI inference or host task execution. |
| V20 | `uv run --frozen --project runtime python evals/run_routing.py --negatives` | PASS | 2026-09-11 | Zero negative firings in every recorded semantic trial; input hashes and predictions are checked offline. |
| V21 | `uv run --frozen --project runtime python scripts/ci/check_budget.py` | PASS | 2026-09-11 | Command passed. |
| V22 | `uv run --frozen --project runtime python scripts/ci/check_no_secrets.py; uv run --frozen --project runtime python scripts/ci/check_history.py` | PASS | 2026-09-11 | Authorized published-history replacement completed. Current-tree and all-ref patch-body scans are clean; an independent fresh remote mirror also has zero findings. Private backups retained. See docs/evidence/published-history-cleanup-2026-09-11.json. |
| V23 | `uv run --frozen --project runtime python scripts/ci/check_licenses.py` | PASS | 2026-09-11 | Command passed. |
| V24 | `CLI_PYTHON scripts/ci/cli_drift.py; .github/workflows/cli-drift.yml; CLI_PYTHON scripts/ci/cli_drift.py` | PARTIAL | 2026-09-11 | Hosted publication run 34632699299 passed and created issue #1. Manual preview and mocked duplicate-handling tests remain recorded. The actual Tuesday scheduled trigger is not yet observed. See docs/evidence/hosted-drift-publication-2026-09-11.json. Owner: repository CI maintainers. |
| V25 | `CLI_PYTHON scripts/check_examples.py --live --profile DEFAULT --region us-chicago-1 --report docs/evidence/validation-cli.json` | FAIL | 2026-09-11 | 36 CLI reads passed; 232 syntax-only examples. Paid-lab sweep: 38 passed, two triage failures (Cloud Guard 404/Support 403), two FinOps coverage gaps, four inert SQL files. See docs/live-validation-2026-09-11.md. Current offline recheck: docs/evidence/second-lab-release-gate-2026-09-11.json; retained live evidence, not a new fixture deployment. The second separate setup attempt returned Cloud Guard HTTP 500 after policy propagation; the temporary policy was removed and disabled state independently confirmed. Owner: OCI operator / skill maintainers. |
| V26 | `OCI_CONFIG_PROFILE=DEFAULT OCI_CLI_PROFILE=DEFAULT uv run --frozen --project runtime oci-readonly-smoke --live --region us-chicago-1` | PASS | 2026-09-11 | 11 selected calls in three benchmark runs: 33/33 passed. Fifteen tools discovered. See docs/evidence/mcp-benchmark-2026-09-11.json. Current offline recheck: docs/evidence/second-lab-release-gate-2026-09-11.json; retained live evidence, not a new fixture deployment. |
| V27 | `claude plugin eval . --threshold 0.8 --json SCRATCH/run.json --output-dir SCRATCH --no-publish --no-scaffold --mocks record --max-cost-usd 1 --runs 1; uv run --frozen --project runtime python scripts/eval/verify_native_reference_benchmark.py evals/results/native-reference-benchmark-2026-09-11.json; CLI_PYTHON scripts/eval/verify_native_command_audit.py evals/results/native-reference-benchmark-2026-09-11.json evals/results/native-reference-command-audit-2026-09-11.json; uv run --frozen --project runtime python scripts/eval/verify_checked_task_benchmark.py evals/results/checked-task-benchmark-2026-09-11.json; CLI_PYTHON scripts/eval/verify_native_command_audit.py evals/results/checked-task-benchmark-2026-09-11.json evals/results/checked-task-command-audit-2026-09-11.json` | PARTIAL | 2026-09-11 | Opt-in checked-command workflow: 35/40; minimum 80%. Earlier reference-only workflow remains 29/40. Fixture answers and observed offline command checks are measured, not complete query semantics or live execution. Native evaluator remains early-access restricted. See docs/checked-task-validation-2026-09-11.md. Subcheck V27-reference: PASS. Subcheck V27-syntax: PASS. Subcheck V27-checked: PASS. Subcheck V27-checked-syntax: PASS. Owner: evaluation maintainers. |
| V28 | `uv run --frozen --project runtime python scripts/eval/head_to_head.py; uv run --frozen --project runtime python scripts/eval/head_to_head.py; uv run --frozen --project runtime python scripts/eval/verify_tool_task_benchmark.py evals/results/tool-task-benchmark-structured-2026-09-11.json` | PARTIAL | 2026-09-11 | Four offline arms and a separate controlled model-backed synthetic MCP measurement are recorded. See docs/tool-task-benchmark.md for 160 attempts, grades, costs and limitations. Original native four-product deployment comparison remains unmeasured. Subcheck V28-offline: PASS. Subcheck V28-fixtures: PASS. Owner: evaluation maintainers. |

PASS refers only to the stated scope. V19/V20 verify dated semantic-classification
evidence, not fresh model execution. V24 has real hosted notification evidence,
but no actual Tuesday scheduler observation. V25/V26 establish selected bounded reads, not complete workloads or
inventories. The [four-arm fixture-tool benchmark](tool-task-benchmark.md) includes
actual model tool calls, but does not instantiate the native products required by
V27/V28. The distributed tree is inspected before runtime-created environment links.
