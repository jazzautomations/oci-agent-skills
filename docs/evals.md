# Evaluation evidence — 2026-09-10

The current selection gate uses **recorded semantic classification** of all 37
skill descriptions. CI verifies the input fingerprints and recomputes scores;
it does not call a model or claim native host task completion.

| Measurement | Result | Criterion |
|---|---:|---|
| Semantic selection, seed 17 | 77/80 (96.25%) | ≥90% in every trial |
| Semantic selection, seed 29 | 76/80 (95.00%) | ≥90% in every trial |
| Overlap pairs | 4/4 in each trial | All four in every trial |
| Negative skill firings | 0/40 seed 17; 1/40 seed 29 | Zero in every trial |
| Additional synthetic boundaries | 12/12 | All correct; development regressions |
| Authored fenced commands | 285/285 | ≥95% syntax validity |
| Guard auto-allow on mutation fixtures | 0/20 | Zero; inert replay |
| Sanitizer fixtures | 10/10 | Flagged, returned, idempotent |

The current **V20 gate fails**: seed 29 selected `oci-navigator` for historical OCI-C
terminology despite its explicit exclusion. Owner: evaluation/routing maintainers.
Both trials are retained; neither the benchmark nor the labels were changed to turn
this into a pass. V19 and the additional boundary collection pass.

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
```

Missing, stale or inconsistent evidence fails. Changes to skill descriptions,
the corpus, remap, policy or collector require new collection. With an
authenticated compatible Claude CLI, make the bounded paid calls explicitly:

```bash
uv run --frozen --project runtime python scripts/eval/semantic.py --collect
uv run --frozen --project runtime python scripts/eval/boundaries.py --collect
uv run --frozen --project runtime python scripts/eval/run.py --json evals/results/offline.json
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

Authored fences and their directly referenced documents are syntax-checked;
retrieved examples do not establish task completion. Safety replay examines
inert strings and never executes mutation fixtures. Sanitizer fixtures do not
establish live injection resistance, scope preservation or absence of leakage.
Zero tenancy mutations in this harness follows from its construction, not from
observed agent safety. A separate reviewed holdout and native host task runs
remain necessary before broader quality claims.
