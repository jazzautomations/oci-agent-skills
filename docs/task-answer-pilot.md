# Paired fixture-answer pilot — September 11, 2026

The same model answered six fixed tasks twice per arm. Both arms scored **12/12**;
the observed answer-score delta is **zero**. This pilot does not establish an
advantage for the repository.

The [frozen cases](../evals/task-answer-pilot.json) cover running instance counts,
currency separation, missing metrics, truncated inventory, unavailable services
and failed mutation attempts in Audit. All observations are synthetic. Exact JSON
expectations are withheld from model inputs and compared after collection.

The with-reference arm receives the corresponding complete SKILL.md; the baseline
does not. Both receive identical task text and observations. Model tools and MCP
servers are disabled, OCI configuration points to absent files, and no model
command is executed. References are injected manually: this does not test skill
discovery, reference routing, command generation, tool use or native activation.

Two predetermined shuffled orders (17 and 29) are order seeds, not model sampling
seeds. Two model sessions run concurrently. All 24 attempts are retained, with no
retries or exclusions. The host reported `claude-sonnet-5`, Claude Code 2.1.268,
and **US$0.25907** total cost, against a requested maximum of US$0.20 per attempt.
CLI metadata is not independent provider attestation. These six author-designed
tasks are a development pilot, not a held-out population or a replacement for
the original 40 task cases.

The [complete trace](../evals/results/task-answer-pilot-2026-09-11.json) includes
input, fixture, collector and reference fingerprints, answers, scores, usage and
timings. Verify locally without model calls:

```bash
uv run --frozen --project runtime python scripts/eval/verify_task_answer_pilot.py evals/results/task-answer-pilot-2026-09-11.json
```

Collection requires an explicit flag and a new output path; existing evidence
cannot be overwritten:

```bash
uv run --frozen --project runtime python scripts/eval/task_answer_pilot.py --collect --report /tmp/oci-task-answer-new-run.json
```

V27 still lacks a qualifying full host-task score; V28 still lacks a matched
four-arm behavioral evaluation. Neither gate is relabeled as passed by this pilot.
