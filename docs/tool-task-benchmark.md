# Four-arm controlled tool-task benchmark — September 11, 2026

All 160 task/arm pairs were attempted, using the original 40 task prompts and the
same closed-world synthetic MCP read tool. There were 154 completed responses and
148 strict passes; six attempts hit the per-attempt model budget. They are retained
as failures without retries. The evidence verifier passes; this means the receipts,
input fingerprints and arithmetic check out, **not** that every model task passed.

| Reference arm | Strict passes | Completed responses | CLI-reported USD | Median host duration |
|---|---:|---:|---:|---:|
| This pack's preselected skill entrypoints | 39/40 | 40/40 | 0.8898402 | 3,443.0 ms |
| adibirzu reference entrypoints | 33/40 | 34/40 | 1.3032272 | 3,134.5 ms |
| Oracle tool-definition reference | 38/40 | 40/40 | 0.8132188 | 2,951.0 ms |
| No reference | 38/40 | 40/40 | 0.3044556 | 3,094.5 ms |

Total reported cost: **USD 3.3107418**. The pack-versus-bare difference is one task
(2.5 percentage points); one run on a small synthetic suite does not demonstrate
statistical superiority. Host durations include successful and budget-limited
attempts with a reported duration. They are not OCI latency or a load test.

## Fixed protocol and scope

The [collector](../scripts/eval/tool_task_benchmark.py) uses claude-sonnet-5, low
effort, order seed 71, two concurrent processes and USD 0.06 requested budget per
attempt. The CLI can overshoot that cap on a final call; actual per-attempt costs
are retained. The aggregate requested allocation was USD 9.60, not the amount spent.

The [original tasks](../evals/tasks.json) are unchanged. A typed output schema is
added identically across arms; it exposes field names/types, not expected values.
[Fixtures](../evals/tool-task-fixtures.json) provide synthetic observations through
36 fixed read topics. Passing a read task requires the correct structured answer
and a receipt for the required tool topic. Strict JSON equality distinguishes
extra findings, wrong facts and missing evidence; it is not semantic equivalence.

All arms have the **same actual MCP tool**. Pack and adibirzu entrypoints are
preselected by the existing fixed task/skill mapping; this does not test routing.
Oracle's arm supplies tool definitions as reference text, not a running Oracle
executor. There is no actual native activation of the competing plugins. The four
destructive requests cannot execute because the harness has no mutation surface;
their review responses are not a live guard or IAM-denial experiment.

The host exposes only the fixture tool plus its structured-output helper. No
builtin shell, file or browsing tools are enabled; strict MCP configuration omits
other servers, credentials are not supplied and no live OCI calls are made. The
fixture server returns fixed data and records read receipts. Source/input hashes,
initialized tool surfaces, tool arguments, receipts, answers and CLI cost/usage
metadata are retained in the [measurement](../evals/results/tool-task-benchmark-structured-2026-09-11.json).

## Failures, not hidden retries

T04 failed exact grading in **all four arms**: the answers identified wide-policy
but returned explanatory strings and non-findings, instead of the required list
containing only its name. T13 failed in the Oracle-reference and bare arms by
including the isolated table's `none` target as a default route. Six adibirzu-arm
attempts exhausted their budget: T01, T09, T10, T23, T24 and T36. The limit was not
raised selectively; the result should not be read as an unconstrained capability
ranking. All failures and costs remain in the common denominator of 40 per arm.

Two aborted instrumentation collections are retained separately and excluded from
the comparison: [10 rows / USD 0.198204](../evals/results/tool-task-benchmark-2026-09-11.json)
used safe mode, which disabled the intended MCP tool; the misleadingly named
[34-row valid file / USD 0.7635494](../evals/results/tool-task-benchmark-valid-2026-09-11.json)
restored the tool but lacked schema-enforced output and was stopped to repair that
protocol. Neither file is a completed or qualifying run. The final collection
was fresh and used the same repaired protocol for every arm, with no selective
case retries. Earlier costs still count toward the session's spending.

## Offline verification and reproduction

```bash
uv run --frozen --project runtime python scripts/eval/verify_tool_task_benchmark.py evals/results/tool-task-benchmark-structured-2026-09-11.json
uv run --frozen --project runtime python scripts/eval/tool_task_benchmark.py --report /tmp/new-tool-task-benchmark.json
```

The second command is a dry-run. Add `--collect` only for a separately budgeted
fresh measurement; an existing report is never overwritten. Verification checks
all 160 unique pairs, source/reference input hashes, protocol metadata, tool calls
against receipts, grades and aggregates. Tests also reject removed receipts and
altered scores. CI makes no new model calls. `complete=false` intentionally means
not all attempts completed successfully, even though all 160 were collected.

This fills the controlled model-backed fixture-tool measurement gap, but is not a
substitute for provider-restricted native V27 or the originally specified native
four-product V28 deployment comparison. See the [release matrix](validation-matrix.md).
