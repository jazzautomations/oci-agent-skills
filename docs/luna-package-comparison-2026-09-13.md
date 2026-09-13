# GPT Luna package comparison — September 13, 2026

**Subsequent command audit found six faulty queries in this package's proposals.**
The 40/40 below is the original fixture/command-syntax score, not successful OCI
command execution. Read the [query validation follow-up](query-validation-2026-09-13.md)
before interpreting this comparison. It does not establish superiority.

**This package achieved the highest observed score: 40/40, versus 36/40 for
official Oracle skills and 36/40 for adibirzu. This is an exploratory result.**
Both competing agents reported truncated skill output and an initial workspace
filename listing outside the instructed boundary. Complete equivalent context
delivery and strict protocol compliance are therefore not established. The
result does not prove general superiority or close the remaining release gates.

| Package | Submitted / schema valid | Primary pass | Exact answer correct | Final commands all checked |
| --- | --- | --- | --- | --- |
| This package | 40 / 40 | 40/40 | 40/40 | 40/40 |
| Oracle skills | 40 / 40 | 36/40 | 36/40 | 40/40 |
| adibirzu OCI skills | 40 / 40 | 36/40 | 39/40 | 39/40 |

The primary criterion combines the original exact answer, required observation
reads, valid inert commands and a successful contract check of every final
command. No failures were rerun and no original answer or grading criterion was
changed. All 120 cases requested a skill entrypoint through the document broker;
none requested additional reference files. A successful broker response does not
prove that its full text survived the orchestration output limit.

## Scope and provenance

At the user's request, three separate orchestrator agents were launched with the
explicit model selection `gpt-5.6-luna`. Each received the same instructions,
original task prompts, output schemas, synthetic observations and inert command
checker, with a different copied package. Each retained one context across its
40 tasks and batched phases of work. These are not 120 independent native plugin
sessions. No OpenCode Zen/MiMo comparison was started; the earlier
[native protocol and local preflights](native-package-comparison-2026-09-13.md)
remain separate evidence.

| Item | Pinned value |
| --- | --- |
| This package source | `55c03146a0ea334124549c4c5a91210228bd83af` |
| [Oracle skills](https://github.com/oracle/skills/tree/b0afa3bfd7c7e3547458d7fe52649ab1b59706b7) | `b0afa3bfd7c7e3547458d7fe52649ab1b59706b7` |
| [adibirzu OCI skills](https://github.com/adibirzu/oci-skills/tree/a4fbf70fd26d1a1c820261a7d4761ebb55457c84) | `a4fbf70fd26d1a1c820261a7d4761ebb55457c84` |
| Registered entrypoints | 37 / 14 / 27; Oracle includes domain routers |
| Task order | Original 40 tasks, shuffle seed 915, one submission per arm/case |
| Broker limits | 16 actions and 8 observation reads per case; 45-minute collection deadline |
| Cost / tokens | Unavailable from this interface; no free-service or billing claim |

The package trees preserved their original skill and reference layout. The
model-facing task payload omitted expected answers. The parent graded final
submissions separately and withheld correctness feedback from the evaluators.
Access boundaries were instructions, not an enforced isolation boundary: broader
orchestrator tools remained available.

## Failures retained

Oracle failed T07 (instance public IPs), T10 (resource availability) and T04
(any-user policies) with wrong-topic observations and incorrect answers. T05
(dynamic groups) added literal backslashes to the matching rule and failed exact
answer comparison. Its command validity and final-command checking passed.

adibirzu failed T10 with an incorrect availability answer and missing required
observation. T18 (boot-volume backups) submitted a corrected final command without
checking that exact version. T04 and T31 (ADB inventory) returned correct answers
but empty command lists for tasks requiring commands. These last three failures
explain the difference between its 39 correct answers and 36 primary passes.

Against each opponent there were four package-only wins and zero opponent-only
wins. The exact two-sided discordant-pair p-value is 0.125, and Holm adjustment
for the two comparisons gives 0.25. This fails the declared 0.05 threshold.
Repeated context and development-task reuse further limit inference; the
descriptive lead cannot be advertised as statistically established superiority.

## Audit and reproduction

The [complete recorded results](../evals/results/luna-package-comparison-2026-09-13.json)
retain all answers, events, grades, source and corpus hashes, protocol deviations
and paired calculations. An independent local replay reproduced all 554 broker
events against unchanged corpus files with matching event/result hashes. Replay
made zero model or cloud calls. The report includes that replay receipt; the
private collector/corpus copies are not distributed as a public replay harness.

The public verifier recomputes all scores, original prompt/schema fingerprints,
observation receipts, command checks and aggregates without inference or command
execution. Run it in the evidence checkout while the measured source hashes
still match:

```bash
uv run --frozen --project runtime python scripts/eval/verify_luna_package_benchmark.py evals/results/luna-package-comparison-2026-09-13.json
```

The verifier rejects changed measured sources and altered recorded claims. Its
unit tests cover omissions, duplicates, source changes, schema/answer changes,
false evidence/check claims, budget violations and statistical claims. It cannot
attest model identity beyond the selected orchestrator model, hidden tool access,
complete context delivery or provider billing.

The post-run agent audit is self-reported. Oracle and adibirzu each reported one
truncated aggregate activation response and an initial read-only `rg --files`
listing outside the broker-only instruction; they reported no gold file-content
reads. All agents reported visible prompts and used observations, and no OCI or
network command execution. These disclosures are retained, not treated as proof
of isolation. No additional model attempts were made to replace these outcomes.

This experiment covers synthetic development tasks and inert command contracts.
It does not test full query semantics, real account permissions, production
outcomes, mutation workflows, reference retrieval quality, repeated held-out
tasks or four native products. V24, V25, V27 and V28 remain governed by the
[validation matrix](validation-matrix.md); this score does not close them.
