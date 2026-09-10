# Evaluation evidence — 2026-09-10

The current selection gate uses **recorded semantic classification** of all 37
skill descriptions. CI verifies the input fingerprints and recomputes scores;
it does not call a model or claim native host task completion.

| Measurement | Result | Criterion |
|---|---:|---|
| Semantic selection, seed 17 | 80/80 (100%) | ≥90% in every trial |
| Semantic selection, seed 29 | 80/80 (100%) | ≥90% in every trial |
| Overlap pairs | 4/4 in each trial | All four in every trial |
| Negative skill firings | 0/40 in each trial | Zero in every trial |
| Additional synthetic boundaries | 31/31 | All correct; development regressions |
| Authored fenced commands | 285/285 | ≥95% syntax validity |
| Guard auto-allow on mutation fixtures | 0/20 | Zero; inert replay |
| Sanitizer fixtures | 10/10 | Flagged, returned, idempotent |

### Current ownership repair

The revised [ownership contracts](routing-contracts.md) distinguish command-name
errors from application capability, tool-executor identity from IAM statements,
backup recovery impact from command mechanics, and generic A1 capacity from an
explicit Free Tier request. The enterprise-apps description explicitly covers
application capability questions while excluding CLI-name errors and UI editing.
The recorded results are **80/80 and 80/80**, with **zero routing disagreements**.
All 80 requests are correct in both trials.
The [verified diagnostic](../evals/results/routing-diagnostics.json) lists every
remaining error and independently distinguishes correctness from agreement.

The original 80 routing prompts, 40 negatives, expected labels, remap, model,
policy, seeds and thresholds are unchanged. All original 15 synthetic cases are
retained; sixteen new development cases exercise adjacent supported and excluded
requests. These are known regression cases, not an unseen holdout.

### Historical errors behind 77/80

Before the repair, R01 (CLI discovery) and R68 (backup retention) failed in both
trials; R60 (agent identity) and R71 (application capability) failed once each.
The [archived diagnostic](../evals/results/routing-diagnostics-before-ownership.json)
and [historical study](routing-reliability.md) retain that four-case analysis.
The first ownership candidate scored 79/80 twice with 25/25 boundaries; its
remaining R01 and R13 disagreements motivated explicit CLI-error and Free Tier
scope clarification. [Development traces](../evals/results/semantic-ownership-development.json)
and [inputs](../evals/results/ownership-development-inputs.json) are retained.
The next candidate reached 80/80 once but failed a negative case in the other
trial; its [rejected traces](../evals/results/semantic-name-scope-development.json)
are preserved. The next published candidate scored 79/80 twice after excluding
database-family selection and Integration visual editing from inappropriate owners.
Its [traces](../evals/results/semantic-capability-development.json) retain the
remaining R01/R71 errors. The final enterprise-description refinement is documented
in [the ownership decision](routing-contracts.md#capability-questions-and-product-name-overlap),
including an invalid-JSON collection attempt and one complete technical retry.
No expected label was reassigned to accommodate a prediction.

### Collection scope

Both V19 and V20 pass after clarifying that `oci-navigator` excludes Compute
Classic/OCI-C terminology and comparisons, including comparisons with current OCI.
The previous 37-skill collection failed V20 and remains available in the
[catalog-expansion trace](../evals/results/semantic-catalog-expansion.json).
The original benchmark, labels, policy, seeds and model are unchanged. The
subsequent ownership repair is described above and retains the Classic exclusions.

The two classifier sessions used `claude-sonnet-5` with tools and MCP disabled.
Positive and negative requests were shuffled together with opaque IDs. The model
received names, descriptions and request text; expected labels and trap metadata
were withheld. Scoring used the unchanged original 80 routing and 40 negative
cases, with the existing skill-merge remap. Both predeclared trials must pass.

Inspect the [main traces](../evals/results/semantic.json),
[boundary trace](../evals/results/semantic-boundaries.json),
[failed development trials](../evals/results/semantic-development.json), and
[research, scope repairs and remaining gaps](semantic-routing.md).
These are development/regression results on known examples, not unseen holdout
performance. CLI-reported session metadata is not independent provider attestation.

## Reproduce

Verify recorded evidence and deterministic component checks without model access:

```bash
uv run --frozen --project runtime python scripts/eval/run.py --json /tmp/oci-evaluation.json
uv run --frozen --project runtime python scripts/eval/semantic.py
uv run --frozen --project runtime python scripts/eval/boundaries.py
uv run --frozen --project runtime python scripts/eval/routing_diagnostics.py --check evals/results/routing-diagnostics.json
```

Missing, stale or inconsistent evidence fails. Changes to skill descriptions,
the corpus, remap, policy or collector require new collection. With an
authenticated compatible Claude CLI, make the bounded paid calls explicitly:

```bash
uv run --frozen --project runtime python scripts/eval/semantic.py --collect
uv run --frozen --project runtime python scripts/eval/boundaries.py --collect
uv run --frozen --project runtime python scripts/eval/run.py --json evals/results/offline.json
uv run --frozen --project runtime python scripts/eval/routing_diagnostics.py --json evals/results/routing-diagnostics.json
```

The policy caps each main trial at USD 0.75 and the boundary run at USD 0.25.
Unavailable models and incomplete runs fail; there is no lexical fallback.

The old lexical matcher remains available through `scripts/eval/run.py --legacy-routing`.
Its archived September 9 result was 37.5%, mostly because a keyword scope filter
rejected implicit requests. That diagnostic is not semantic accuracy and no
longer determines V19. The [archived comparison](head-to-head.md) keeps the same
lexical method for all four arms; semantic scores must not be mixed into that
table. The [older single-run model labels](routing-model-eval.md) also remain
archived, with their original provenance limits.

## Corpus and scope of the claims

The task records are imported unchanged into tasks.json, case.yaml, prompt.md
and the skill-creator evals.json shape. Re-import with
`uv run --frozen --project runtime python scripts/eval/import_corpus.py` from the
frozen `evals/corpus/eval-corpus.json`. Tests compare every imported row to that
source, including in fresh clones. `remap.json` applies the four planned skill
merges. Research command shapes are retained as evidence, not assumed correct.

`claude plugin eval` returned an early-access restriction in the dated
[host diagnostic](../evals/results/host.json). The YAML grader keys remain
unverified. Isolated selection does not establish V27's ≥0.8 agent task score or
close V28's four-arm behavioral comparison.

The original design accepts a skill-creator **task evaluation** as a substitute
for the unavailable native evaluator. That alternative remains unmeasured.
Its description-trigger evaluator is not sufficient: qualifying evidence needs
matched with-skill and baseline task attempts with observable, independently
graded outcomes. The provider restriction alone does not explain this open gate.

Authored fences and their directly referenced documents are syntax-checked;
retrieved examples do not establish task completion. Safety replay examines
inert strings and never executes mutation fixtures. Sanitizer fixtures do not
establish live injection resistance, scope preservation or absence of leakage.
Zero tenancy mutations in this harness follows from its construction, not from
observed agent safety. A separate reviewed holdout and native host task runs
remain necessary before broader quality claims.
