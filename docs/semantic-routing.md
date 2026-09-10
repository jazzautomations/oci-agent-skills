# Semantic selection: investigation and evaluation design

The 37.5% figure came from a lexical evaluator, not from the installed agent.
`scripts/eval/graders.py` is imported by evaluation scripts only. The native host
selects skills using its own model and context; the package's MCP and guard do
not call this lexical selector.

## What failed

The archived lexical baseline at `1802198` gets 30 of 80 routing cases right.
Among its 50 errors:

| Cause | Cases | Mechanism |
|---|---:|---|
| Context filter rejection | 39 | A regular expression requires explicit product vocabulary before comparing descriptions |
| Wrong lexical match | 11 | Shared words outweigh the intended action or service boundary |
| Low lexical score after passing the filter | 0 | The score cutoff is not the dominant failure here |

The tokenizer also removes every trailing `s`, turning `DNS` into `dn` and
`access` into `acce`. This is not linguistic stemming. These are defects in the
measurement instrument, not proof that all 33 skill descriptions are defective.
The old selector and reports are retained as a frozen, explicitly limited
comparison baseline; they must not be represented as semantic or host accuracy.

## What the research supports

Semantic retrieval encodes meaning and can recover synonyms that lexical search
misses. A common architecture retrieves candidates with a bi-encoder and then
scores query/candidate pairs with a cross-encoder. Retrieval is useful at large
scale; for small candidate sets, scoring all candidates avoids dropping the
correct one before reranking. [Sentence Transformers: retrieve and rerank](https://www.sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html).

For normalized vectors, cosine similarity is their dot product. That score is
not a calibrated probability that the request is supported. Choosing the nearest
candidate always produces a winner, including for unsupported requests. The
CLINC out-of-scope study evaluates unsupported intents separately and finds that
they remain difficult even when in-scope classification is strong.
[Larson et al., EMNLP-IJCNLP 2019](https://arxiv.org/abs/1909.02027).

Model-based assessment and deterministic grading serve different purposes.
Keep the inputs, trials and outputs, then score the observed result. Multiple
trials help expose variability; a component selection test still does not
establish an agent's task outcome.
[Anthropic: demystifying evaluations](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents).

Do not fit thresholds, dictionaries or prompts using the expected answers and
then report the same examples as unseen generalization. Calibration requires
separate data. The existing corpus has already been inspected by maintainers;
it is a regression benchmark, not a newly blinded holdout.
[scikit-learn: data leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage).

## Decision for this repository

For 33 descriptions, evaluate a direct semantic classifier against the complete
catalog. An embeddings index would add a retrieval cutoff and calibration work
without an established scale requirement. A parse tree can be useful for a
structured query language; it does not itself resolve informal Portuguese,
implicit context or overlapping service ownership. Huffman coding and Mersenne
primes do not address the observed failure mechanism.

The classifier is an evaluation instrument, not a new dependency in the MCP
runtime or a replacement for the native host's routing. It receives only full
skill names/descriptions and request text. It must select an exact name or JSON
`null`. It receives no tools and performs no OCI operations.

The [policy](../evals/semantic-policy.json), fixed before each collection, pins the model, two trial
orders, prompt, budget and unchanged numerical criteria. Case IDs are replaced
with neutral IDs; positive and negative requests are shuffled together. Expected
labels, trap metadata and the original R/N prefixes never enter the model input.
Every trial must meet ≥90% routing accuracy, all four overlap pairs and zero
negative firings. A best-of-two score is not accepted.

Collect with the authenticated Claude CLI and the locked Python environment:

```bash
uv run --frozen --project runtime python scripts/eval/semantic.py --collect
```

Collection makes bounded paid model calls; the policy caps each call at USD 0.75.
It uses safe mode, no tools, no MCP servers, no project settings or persistent
session, a temporary working directory and absent OCI config selectors. It
records model/session metadata, sanitized outputs, request hashes and costs.
An unavailable model or incomplete response is a failed collection, not a pass.

Verify a saved report without credentials or model calls:

```bash
uv run --frozen --project runtime python scripts/eval/semantic.py
```

Verification recomputes every score from saved selections. Changing descriptions,
the corpus, remap, collector or policy makes the evidence stale. Missing trials,
duplicate IDs or sessions, unknown skill names, tool use and altered scores are
rejected. This establishes consistency of dated evidence, not an independent
provider attestation or a fresh inference on the CI runner.

## Remaining gaps

- A new separately authored, reviewed holdout is needed for a generalization claim.
- Two trials measure limited order sensitivity, not complete stochastic stability.
- Batch classification differs from an individual interactive host request.
- Some reference labels deserve a separate ownership review. For example, R68
  expects disaster recovery for a single boot-volume backup-policy request,
  while the current DR description delegates a single service's backup command.
  The strict original label is retained and counted as an error if missed; it is
  not silently changed into a permissive accepted-answer list during this repair.
- Native skill activation, successful task completion and behavior under live
  tool output remain V27/V28 work; this component test does not close them.
- If the catalog grows substantially, compare multilingual embeddings and a
  reranker using recall@k, accuracy, out-of-scope false positives, latency and cost.
  Calibrate similarity and ambiguity margins on separate development data.

## Scope repairs supported by product contracts

The first two semantic trials exposed six and seven negative firings. Most
came from the fleet description's broad reference to MySQL, PostgreSQL and
general DBA lifecycle without requiring an OCI service or management context.
The repaired description distinguishes managed services and enrolled external
databases from standalone engine administration. This preserves Oracle's
supported external-database management, including on-premises databases.
[Oracle: external database systems](https://docs.oracle.com/en-us/iaas/database-management/doc/database-management-external-database-systems.html),
[OCI Database with PostgreSQL](https://docs.oracle.com/en-us/iaas/Content/postgresql/).

The enterprise skill now distinguishes explaining the service/application API
boundary from performing application UI authoring. Oracle documents Integration
instance lifecycle separately from design-time integration APIs. The navigator
owns discovery and command-name errors; the enterprise skill owns application
API reach. The database skill owns database-family noun mapping.
[Oracle Integration instance lifecycle](https://docs.oracle.com/en-us/iaas/application-integration/doc/stopping-and-starting-instance.html),
[Oracle Integration application API requests](https://docs.oracle.com/en/cloud/paas/application-integration/rest-api/SendRequests.html).

Only these three skill scopes were edited. The first before/after comparison
retained the same classifier prompt, model, trial orders, original 80/40 corpus
and scoring thresholds. It reduced negative firings from 6/7 to 1/2, while
scoring 78/80 and 77/80. The remaining mistakes ignored explicit exclusions.
Policy version 2 adds an action-applicability check and makes applicable
exclusions veto selection, even when a product name matches. It introduces no
per-case rule, examples or expected labels. Model, trial orders and acceptance
thresholds remain fixed. These iterations use development feedback; their
regression scores are not claimed as unseen validation.
The additional [boundary cases](../evals/semantic-boundaries.json) include the
important positive counterexample: an on-premises database enrolled in OCI
management must remain eligible. Collect those additional regressions with
`uv run --frozen --project runtime python scripts/eval/boundaries.py --collect`;
check the saved result with the same command without `--collect`. This additional
call is capped at USD 0.25. CI rejects missing, stale or failing boundary evidence.

## Recorded outcome — September 10

| Configuration | Correct selections, seeds 17 / 29 | Negative firings, seeds 17 / 29 | Both trials pass? |
|---|---:|---:|---|
| Original descriptions, policy 1 | 74/80 · 76/80 | 6/40 · 7/40 | No |
| Three scope repairs, policy 1 | 78/80 · 77/80 | 1/40 · 2/40 | No |
| Three scope repairs, policy 2 | 79/80 · 77/80 | 0/40 · 0/40 | Yes |

The final two trials each resolve all four overlap pairs. The additional twelve
synthetic boundaries also pass under policy 2. The model is `claude-sonnet-5`;
the final main collection completed at 03:35 UTC on September 10, 2026.
The [current traces](../evals/results/semantic.json) and
[boundary trace](../evals/results/semantic-boundaries.json) include the saved
selections used by the verifier. The
[development history](../evals/results/semantic-development.json) preserves the
failed iterations instead of presenting only the successful configuration.

The improvement combines better skill contracts with a better evaluation
instrument. It does not isolate a causal gain in the native host or establish
generalization beyond the inspected benchmark. Acceptance thresholds and the
original prompts and expected labels were not changed.
