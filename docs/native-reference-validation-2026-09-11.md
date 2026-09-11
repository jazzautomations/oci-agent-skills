# Reference-enabled native evaluation — September 11, 2026

This follow-up removes the previous harness's blanket file-access restriction.
It preserves the earlier collector, responses and grades. It does not equate
fixture-answer correctness, command syntax or a review-file format with full
end-to-end task completion.

## Results

All **80 attempts** were collected, with failures retained. The
[original records](../evals/results/native-reference-benchmark-2026-09-11.json),
[pinned syntax audit](../evals/results/native-reference-command-audit-2026-09-11.json)
and [skill-creator-format summary](../evals/results/native-reference-skill-creator-2026-09-11.json)
are checked in. This measurement is **below V27's 80% minimum**, before any
additional original-task semantic requirements; V27 is FAIL, not merely blocked
by the native evaluator's early-access restriction.

| Measurement | Native plugin + Read | No plugin |
|---|---:|---:|
| Attempts | 40 | 40 |
| Protocol-accepted responses | 38 | 40 |
| Successful native Skill activations, including rejected aliases | 29 | 0 |
| Successful reference reads in task collection | 0 | 0 |
| Original answer + receipt + command-shape passes | 29/40 | 24/40 |
| After common pinned syntax audit | 29/40 (72.5%) | 13/40 (32.5%) |
| Median host-reported duration | 5.317 s | 4.118 s |
| Median collector wall duration, including host startup | 9.338 s | 7.527 s |
| Reported model charge | $2.5107282 | $0.5320918 |

The task-level difference is +40 percentage points under this limited rubric,
not evidence of 100% correctness or general superiority. Eleven baseline grades
changed under the common stricter audit; native grades did not change. Allowing
reference access did **not** cause any task to use Read. The successful preflight
must not be mixed into that zero-read result.

Native failures: T14/T17 used unqualified Skill names and were rejected by the
collection protocol despite successful host results; T04/T13 failed exact fixture
answers; T02/T03/T07/T20/T26/T30/T36 failed command-shape requirements. Those are
different failure classes, not eleven failed OCI service calls. Further semantic
review is still necessary even for syntax passes: T18's proposal filters
`lifecycleState`, whereas the package's CLI examples use `"lifecycle-state"`.
The syntax grader does not establish that the requested backup is selected.

Collection cost was **$3.04282**. Both access preflights added **$0.1513524**:
this follow-up totals **$3.1941724**, bringing known cumulative model charges to
**$10.8378692**. Earlier OCI compute estimates remain below about $1.05, before
storage, taxes and billing reconciliation; uncaptured canceled calls may exist.
This is not a final invoice or a renewed $20 allowance. No new paid OCI resource
was created in this follow-up.

## Protocol

The [collector](../scripts/eval/native_reference_benchmark.py) uses the original
40 task prompts and schemas, one fresh session per task/arm, `claude-sonnet-5`,
low effort and randomized interleaving with seed 83. Both arms receive the same
fixed synthetic MCP observations. The native arm loads a fresh copied plugin;
the baseline has neither plugin nor file tools. No OCI credentials, shell,
generic executor, cloud writes or native competitor servers are available.

The native arm adds only `skills/` and `references/` to the host's restricted
readable directories. It never adds the whole plugin: installation also contains
`evals/`, including golden answers. Explicit denials cover session files and
the plugin's evals, docs and scripts. Reads outside the two authorized trees
cannot receive completion credit. Source fingerprints cover all readable
source files and the installer that rewrites shared-reference links.

A separate [access preflight](evidence/native-reference-access-2026-09-11.json) proved one successful reference read and a denied
read of a harmless canary in `evals/`. An earlier preflight skipped both reads
and therefore failed the access check despite answering its synthetic question.
Neither preflight is counted among the paired task scores; both charges count
toward the ongoing budget. The native host, not prompt text alone, enforces
[restricted directory access and path rules](https://code.claude.com/docs/en/permissions).

The collection has a $6 admission budget inside the user's unchanged aggregate
$20 ceiling. Each attempt requests a $0.10 host cap; admission reserves $0.25 per
concurrent attempt because host caps are checked between requests, not hard
billing ceilings. Unknown billing evidence stops admission. Failed attempts are
retained without retries. A full collection does not imply every response passed.

## Review and reproducibility

The [evidence verifier](../scripts/eval/verify_native_reference_benchmark.py)
checks task pairs, source hashes, exact launch options, tool surfaces, native
activation, reference reads, observation receipts, original grades and billing.
The existing pinned-CLI auditor applies the same stricter syntax rules to both
arms; model-proposed commands are never executed.

The [review exporter](../scripts/eval/export_skill_creator_review.py) creates
per-task `eval_metadata.json`, `grading.json`, outputs and timing. It uses the
official Anthropic skill-creator aggregator and static viewer, pinned to
[`34040c9c568585f6929bedeaad110ad08f079624`](https://github.com/anthropics/skills/tree/34040c9c568585f6929bedeaad110ad08f079624/skills/skill-creator).
Upstream placeholder model/run-count metadata is replaced with captured values;
token counts include recorded cache usage rather than output-character proxies.
One conjunctive assertion per task avoids inflating scores with easy subchecks.
The static viewer is generated locally; no feedback server or deployment is started.

Download the three pinned files listed in `UPSTREAM_FILES` into a separate local
upstream directory; their hashes are checked before import. Reproduce without
new model or OCI calls:

```bash
uv run --frozen --project runtime python scripts/eval/verify_native_reference_benchmark.py evals/results/native-reference-benchmark-2026-09-11.json
```

With Python from the pinned `oci-cli==3.91.0` environment:

```bash
python scripts/eval/verify_native_command_audit.py evals/results/native-reference-benchmark-2026-09-11.json evals/results/native-reference-command-audit-2026-09-11.json
```

After that audit, use an absent output directory:

```bash
uv run --frozen --project runtime python scripts/eval/export_skill_creator_review.py evals/results/native-reference-benchmark-2026-09-11.json evals/results/native-reference-command-audit-2026-09-11.json --upstream-dir /path/to/pinned/skill-creator --output-dir /tmp/oci-reference-review-new
```

## Interpretation limits

- File permission is not evidence that the model actually followed references.
  Count successful `Read` receipts separately from advertised capabilities.
- Fixture answers can be correct while proposed queries omit requested fields
  or use a wrong field name. Syntax alone does not grade query semantics.
- The paired comparison changes plugin availability and Read together. It does
  not isolate the causal effect of references or prove improvement over the
  earlier non-paired collection.
- Unqualified Skill invocations remain protocol rejections even when the host
  returned success; they are not silently relabeled as host or budget failures.
- Task-level dispersion is not repeated-run uncertainty. One development run
  per arm is neither a holdout nor a significance test.
- The upstream review format is useful evidence, not automatic acceptance of
  the original V27 rubric. Independent original-task semantics, scope, leakage,
  silent omission and over-refusal remain distinct from this fixture score.
- V28's original native four-product comparison and live workload claims are
  not replaced by this experiment. No all-green release claim is made.
