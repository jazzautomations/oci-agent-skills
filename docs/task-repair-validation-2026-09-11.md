# Task repairs — September 11, 2026

Five skill bodies and the offline MCP checker were corrected after the previous
35/40 measurement. Names/descriptions and the original task fixtures are unchanged.
The full 40-task score is now **unmeasured for the changed sources**, not silently
inherited from the previous revision. No new cloud resources or IAM changes were
made. This is an implementation repair plus a small development regression.

The [final local checks](evidence/task-repair-final-checks-2026-09-11.json)
passed 565 tests with three warnings and validated 269 offline examples.
The [full matrix recheck](evidence/task-repair-release-gate-2026-09-11.json)
retains four nonpassing criteria; its earlier suite count is preserved separately.

## Changes that shipped

- Authentication no longer recommends silently replacing a bounded page with
  `--all`; the subscription proposal drops that option and its historical live
  label is explicitly dated.
- Security posture filters out policies whose matching-statement list is empty.
  Actual authored JMESPath is tested on CLI-shaped records, with findings kept
  separate from nonfindings and explanations.
- Networking now includes a VCN-scoped IPv4/IPv6 default-route projection. It
  excludes isolated/private-only tables and retains observed target identifiers,
  rather than inventing a target called `none`.
- Monitoring explains that changing the final MQL string invalidates an earlier
  check; budget guidance preserves the canonical leaf and projection and does
  not infer a currency or alert threshold from absent fields.
- Invalid proposals now produce MCP `isError: true` with the existing redacted
  diagnostics, not a normal-success result containing `valid: false`. Actual
  stdio tests verify both valid and rejected proposals; no command executes.

The `skill-creator` review guided narrow fixes and removal of duplicated safety
prose. Essential untrusted-data boundaries stay in the bodies, linked to the
existing shared contract. The generic skill validator rejects the pre-existing
`compatibility` field; it was not removed to satisfy that incompatible schema.
Repository frontmatter, portability and size checks validate the supported format.

## Measured regression, not a full benchmark

The [collector](../scripts/eval/task_repair_regression.py) selected exactly the
five previously failed native cases, before collection. It made one fresh
attempt per case/arm, randomized with seed 83, using the same model, effort,
synthetic observations, restricted tools, original prompts/schemas and strict
checked-workflow rubric. Both arms receive the checker. Failures are retained;
there were no retries, discarded runs or after-the-fact threshold changes.

| Known failing case | Changed plugin + checker | No plugin + checker |
|---|---|---|
| T01: identity | PASS | PASS |
| T04: broad-policy findings | FAIL | FAIL |
| T13: default routes | PASS | FAIL |
| T23: CPU metrics | PASS | PASS |
| T26: budgets | PASS | PASS |
| Total | **4/5** | **3/5** |

All ten attempts completed. All five native attempts activated a skill; none
read a reference. For T04, the native answer identified the observed broad policy
and quoted its statement correctly, but appended an explanation instead of the
literal identifier required by the retained exact-answer rubric. This manual
description does not change FAIL to PASS. The baseline repeated the invented
isolated-route entry in T13. Four recovered development cases do not establish
general superiority, repeatability, held-out relevance or live OCI task success.

Median host duration was 11.728 seconds native versus 8.661 seconds baseline;
median wall duration including startup was 16.561 versus 16.911 seconds.
The native arm cost $0.3884032 and the baseline $0.1140254. Five observations per
arm are not enough to claim a stable latency advantage.

Cost was **$0.5024286**, inside the $1.25 allocation. Known cumulative model charges
are **$15.12589**, plus earlier OCI compute estimates below approximately $1.05,
before storage, taxes, possible uncaptured canceled calls and final invoice
reconciliation. The original aggregate authorization remains $20. No further
paid collection is included in this repair.

## Historical evidence now remains reproducible during maintenance

The [allowlist](../evals/historical-evidence.json) pins five exact report contents
to commit `0cd2730f8677de909267db57baf8a135458646b2`. The
[replayer](../scripts/eval/historical_evidence.py) extracts that local immutable
revision, verifies the supplied report against its stored copy and invokes only
its original offline verifier. It does not fetch code, invoke model/cloud tools,
accept a report-selected executable, modify the checkout or rewrite history.

The original verifiers still recompute inputs, receipts, grades and costs. Their
results are augmented with `historical_replay`, `evidence_revision`,
`current_sources` and changed paths. Altered reports cannot use the historical
path; missing Git history fails closed. A source checkout with the pinned commit
is required; a copied plugin without `.git` cannot replay historical reports.

This separates **evidence integrity** from **current behavioral validation**.
The full release gate marks V27 UNMEASURED after source changes; passing the new
five-case integrity subcheck does not close it. Old reports, failed attempts and
scores are unchanged. A fresh full measurement would be a separately dated report.

## Reproduce

These commands perform no inference or OCI operations:

```bash
uv run --frozen --project runtime python scripts/eval/task_repair_regression.py --report evals/results/task-repair-regression-2026-09-11.json
uv run --frozen --project runtime pytest -q tests/test_task_repairs.py tests/test_task_repair_regression.py tests/test_historical_evidence.py tests/test_read_contract.py
uv run --frozen --project runtime python scripts/eval/verify_checked_task_benchmark.py evals/results/checked-task-benchmark-2026-09-11.json
```

[Raw regression](../evals/results/task-repair-regression-2026-09-11.json) retains
all responses, receipts, source hashes, timings, grades and costs. Full release
readiness also still requires service prerequisites (Cloud Guard, Support and
FinOps), the actual Tuesday scheduler event and the native four-product comparison.
