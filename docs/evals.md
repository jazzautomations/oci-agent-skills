# Evaluation evidence — 2026-09-09

Run `uv run --frozen --project runtime python scripts/eval/run.py --json evals/results/offline.json`.
The command intentionally exits 1 while V19 is red. `uv run --frozen --project runtime python evals/run_routing.py --negatives` isolates V20.

| Measurement | Result | Gate |
|---|---:|---|
| Description routing | 37.5% over 80 | FAIL: ≥90% required |
| Overlap pairs | 4/4 | PASS |
| Negative skill firings | 0/40 | PASS: zero required |
| Authored fenced commands | 100.0% of 275 | PASS: ≥95% required |
| Guard auto-allow on mutation fixtures | 0/20 | PASS: zero required |
| Sanitizer fixtures flagged, returned, idempotent | 10/10 | PASS |

These are deterministic offline proxies. The selector uses the same scope filter and description matcher for every arm, never case IDs or expected labels. Its conservative context filter and lexical matching miss many implicit and Portuguese requests. **V19 remains a release blocker, owned by evaluation/routing maintainers.** Do not tune against expected labels or call this host routing accuracy. The source prompts and the plan's descriptions remain unchanged.

The task records are imported unchanged into tasks.json, case.yaml, prompt.md and the skill-creator evals.json shape. remap.json records the four planned skill merges. Re-import with `uv run --frozen --project runtime python scripts/eval/import_corpus.py` when the build-only research checkout is available. Tests compare every imported row to that source. The research command shapes are retained as evidence, not assumed correct.

`claude plugin eval . --threshold 0.8 --json evals/results/run.json` returned “plugin eval is currently in early access”. See evals/results/host.json. The YAML grader keys remain unverified. The skill-creator JSON format is supplied, but no model-backed skill-creator run was performed; the offline substitute cannot establish V27's ≥0.8 agent score.

Commands are linted from authored skill/reference fences; task retrieval records show selected examples, not task completion. Safety replay inspects inert strings five times per T37–T40 and never executes them. Sanitizer evidence does not establish task completion, scope preservation, leakage, silent-drop, over-refusal or resistance to live injection. Those behavioral outcomes remain unmeasured. Actual tenancy mutations during this harness are zero by construction, not a behavioral safety score.
