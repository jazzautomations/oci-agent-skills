# Command-query validation follow-up — September 13, 2026

**The Luna 40/40 score does not establish correct OCI commands.** A new offline
response-field audit found six faulty command queries in this package's recorded
answers. The original score and transcripts are preserved; their criterion used
normalized fixture observations plus command syntax, not actual query results.
No claim of complete validation or superiority follows from that score.

| Package | Proposed commands audited | Known field/type errors | Field check passed |
| --- | --- | --- | --- |
| This package | 36 | 6 | 30 |
| Oracle skills | 36 | 1 | 35 |
| adibirzu OCI skills | 34 | 6 | 28 |

All 106 recorded command queries were inspected. Twelve safety-task responses
intentionally contained no commands; adibirzu also omitted commands in two read
tasks, already counted as failures by the original scorer. These are command
counts, not a new end-to-end task leaderboard. Returning an entire valid `data`
object passes the field check even when the command does not solve the task.

## Six failures and tested query corrections

| Task | Recorded issue | Tested correction |
| --- | --- | --- |
| T14 public buckets | Bucket summaries have no `public-access-type` | Read each bucket's details with `bucket get` before classifying its access |
| T15 lifecycle | `bucket get` has no `lifecycle-policy` field | Use `object-lifecycle-policy get` and `data.items`; handle the actual service status separately |
| T16 object prefix | The CLI flattens objects under `data`, unlike the SDK's `ListObjects.objects` envelope | Read `data[]` and retain sibling `next-start-with`; a bounded page is not a complete count |
| T24 alarms | `enabled` is absent | Read `"is-enabled"` |
| T29 node pools | `"node-config-details.size"` means one literal field | Read `"node-config-details".size` |
| T33 Cloud Guard | Collection flattened as an array, plus incorrect item names | Read `data.items[]`, with `"resource-name"`, `"risk-level"` and the required lifecycle fields |

Fourteen regression cases cover these corrections on representative response
objects, invalid syntax/types, dynamic fields and unsupported expressions.
These tests execute JMESPath locally. They do not execute the recorded commands,
rerun the model, overwrite its answers or establish live service success.

The affected skill examples already use the appropriate endpoints/fields; the
model did not consistently follow them. The correction here closes a gap in
validation rather than retroactively turning its proposals into successful runs.

## Reproducible checks added

The [pinned response contracts](../evals/query-response-contracts.json) cover all
35 distinct command paths proposed in this experiment. They derive field/type
trees from OCI SDK 2.185.0 and CLI 3.91.0, check field names against the CLI
serializer and retain source hashes for 150 SDK models. The Object Storage CLI
adapter is explicit: its renderer moves objects to `data` and retains pagination
metadata alongside it. Composite VNIC reads produce VNIC objects. Custom CLI
callbacks were inspected for delegation or response reshaping.

Regenerate/check contracts with Python from the pinned OCI CLI environment:

```bash
python scripts/generate_query_response_contracts.py --check
```

Recompute the [recorded field audit](../evals/results/luna-query-field-audit-2026-09-13.json):

```bash
uv run --frozen --project runtime python scripts/eval/audit_query_fields.py evals/results/luna-package-comparison-2026-09-13.json --output /tmp/luna-query-field-audit.json
```

The audit exits nonzero because failures are retained. Its output hashes the
original report and the response contracts. It does not alter original grading.
The original Luna score verifier now also prints this independent field-audit
summary, so a successful historical score replay cannot hide the newly found
command failures.

CI now checks contract regeneration and scans authored skills/shared references
for proven field errors. The current scan passes 56 queries, leaves 20 expressions
unverified and identifies 210 commands outside its contract coverage; none of
these last two groups is certified. Unsupported expressions and dynamic/recursive
types remain explicit gaps. This is not a general JMESPath type checker.

## Actual remaining release dependencies

The [fresh service and scheduler record](evidence/query-validation-followup-2026-09-13.json)
preserves seven bounded OCI read attempts, including a failed collector request
and its corrected follow-up. No tenancy mutations or new inference occurred.

Cloud Guard remains `DISABLED`. Support still returns HTTP 403 with the selected
user and home region supplied. The selected user has a verified email; that does
not prove Support entitlement or identify the missing permission. Budget and
settled regional cost samples remain empty. The first cost probe omitted a filter
operator and returned 400; the corrected request succeeded with zero rows. Empty
evidence cannot establish savings, forecasts or complete billing behavior.

The weekly workflow is active but has only manual runs. Its next nominal schedule
is September 15, 2026 at 06:17 UTC; actual dispatch is controlled by GitHub. No
schedule was changed just to obtain a green result.

V24 therefore still needs a real scheduled event. V25 needs working service access
and sufficient account evidence. V27 needs a current complete task workflow with
query semantics, filtering, scope, paging and joins checked. V28 still needs the
original native alternatives under comparable conditions. Luna's document-broker
experiment does not supply native product execution. These gates remain open;
passing the new field checks does not waive them.
