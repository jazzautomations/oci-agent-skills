# Checked-command task validation — September 11, 2026

The repository now ships an [optional offline command-contract helper](command-contract.md)
and a separate two-tool MCP transport. It inspects 3,601 read-only leaves from
the pinned OCI CLI 3.91.0 catalog: required flags, declared aliases, enums,
pagination and JMESPath syntax. No OCI configuration is opened and no proposed
command or service callback executes. The default 15-tool server and IAM are
unchanged. This is an opt-in workflow, not an improvement silently applied to
every default plugin session.

## Paired results

All 80 attempts completed; none were retried or discarded. Both arms received
the same offline checker, synthetic observations and generic check/repair
instructions. The native arm additionally loaded the copied plugin with Skill
and restricted reference access. Original prompts, schemas, exact-answer grades
and observation requirements were retained. A pass also required contract-valid
commands and a successful observed check of each exact final command string.

| Measurement | Native plugin + checker | No plugin + checker |
|---|---:|---:|
| Attempts / accepted responses | 40/40 | 40/40 |
| Full checked-workflow passes | **35/40 (87.5%)** | **38/40 (95%)** |
| Successful native activations | 31 | 0 |
| Successful reference reads | 0 | 0 |
| Median host-reported duration | 7.092 s | 7.1515 s |
| Median wall duration including startup | 11.0495 s | 11.8135 s |
| Reported model charge | $2.8678536 | $0.8220892 |

The native arm scored **7.5 percentage points lower** and cost more than the
checker-enabled baseline. This does not support a superiority claim. Relative
to the [earlier reference-only workflow](native-reference-validation-2026-09-11.md),
native passes increased from 29 to 35, but checker access, instructions and the
alias protocol changed together. One development run per task is not a holdout,
a causal ablation or a repeated-run reliability estimate.

The separate pinned-CLI syntax audit yields 37/40 native and 38/40 baseline
under its older rubric. That audit omits the exact final-check receipt and the
new blanket `--all` prohibition; **37/40 is not the checked-workflow score**.
The actual score remains 35/40. Earlier reports and grades are unchanged.

## Failures retained

| Case | Arm | Failure |
|---|---|---|
| T01 | Native | Added an unchecked final region-subscription command using `--all`. |
| T04 | Both | Exact findings were wrong; native also triggered the retained legacy command-shape rejection of a quoted logical operator. The new syntax checker accepts that operator, but the incorrect answer still fails. |
| T13 | Both | Invented a `none` default-route entry for the isolated table. |
| T23 | Native | Changed the metrics query after checking; final command was never checked. |
| T26 | Native | Checked a budget-list command but ignored its missing-query diagnostic. |

The collector now accepts an unqualified skill alias only when one registered
plugin name matches and the host demonstrably loaded that installed skill body.
Regression tests cover accepted, missing-body, ambiguous and foreign identities.
This run used only qualified names, so it does **not** provide a new live
unqualified-alias measurement. The earlier rejected alias attempts remain as
recorded. No task read a reference, despite having permission to do so.

## Scope, provenance and cost

The [collector](../scripts/eval/checked_task_benchmark.py) uses `claude-sonnet-5`,
low effort, seed 83, one session per task/arm and concurrency two. Its source
fingerprints cover prompts, fixtures, installed skill/reference files, previous
collectors, checker/server/generator, metadata, installer and runtime lock.
Golden answers are not readable by the model. Fixed MCP observations are
synthetic, not the output of model-proposed OCI commands. Private raw transcripts
are retained outside the repository and linked by hashes.

Collection cost was **$3.6899428**. Two checked-workflow preflight calls added
**$0.0956494**, totaling **$3.7855922** for this follow-up. Known cumulative model
charges are **$14.6234614**. Earlier OCI compute estimates remain below about
$1.05, before storage, taxes and invoice reconciliation; uncaptured canceled
calls may exist. This is not a final invoice or a new $20 allowance. No new OCI
resources, IAM changes, Vercel configuration or deployments were made here.
The collection's $5 admission allocation and $0.25 reservation per attempt
stayed inside the unchanged aggregate ceiling; host caps are not hard billing
ceilings. No further paid measurement is needed to reproduce these reports.
The [machine-readable summary](evidence/checked-task-summary-2026-09-11.json)
records timings, tool-call counts and the private preflight record's fingerprint.

Syntax passes do not certify query meaning, requested response fields, callback
requirements, authorization, complete inventories or live workload outcomes.
The checker is advisory and is not an execution gateway. Fixture answers can
be correct while a proposed command would answer a different question.
V27 is **PARTIAL for this opt-in workflow**, with its limited 80% minimum met;
the earlier default/reference-only measurement remains below threshold.
Full original-task semantics, V28's native four-product comparison, the actual
Tuesday scheduler event and blocked live service prerequisites remain open.

## Reproduce without paid calls

The [recorded attempts](../evals/results/checked-task-benchmark-2026-09-11.json)
and [independent syntax audit](../evals/results/checked-task-command-audit-2026-09-11.json)
are verified in CI. The verifier checks full task pairs, source hashes, exact
launch grants, plugin identities, observations, final checks, scores and costs.

```bash
uv run --frozen --project runtime python scripts/eval/verify_checked_task_benchmark.py evals/results/checked-task-benchmark-2026-09-11.json
uv run --frozen --project runtime pytest -q tests/test_read_contract.py tests/test_checked_task_benchmark.py
```

Using Python from the pinned OCI CLI environment, without executing proposals:

```bash
python scripts/generate_read_contracts.py --check
python scripts/eval/verify_native_command_audit.py evals/results/checked-task-benchmark-2026-09-11.json evals/results/checked-task-command-audit-2026-09-11.json
```
