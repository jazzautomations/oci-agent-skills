# Foundation progress

- W01 done: JSONL catalog, strict read subset, service index, bounded query helper and catalog tests. Inventory scope and import errors live in `catalog/cli-meta.json` and `catalog/index.json`.
- Validation: `uv run --frozen --project runtime pytest -q tests` — 47 passed. Two generator runs produced byte-identical CLI artifacts (CLI 3.91.0).
- W02 done: Bash advisory guard, redaction, shared shell/Python read-only execution wrapper, catalog replay, 60 shell forms and 20 opaque-form tests. Non-OCI rules are explicitly unmeasured.
- W02 validation: full suite passed (135 tests including W04 validator fixtures); leaf matrix is recorded in `catalog/guard.json`.
- Next exact step: complete W04 live-help checks and commit template, validators and CI with an explicit legacy findings baseline.
- Tool count decision: consolidate limit discovery and values into one MCP tool so all six requested additions fit the fourteen-tool surface.
- Environment: duplicate execution of this identical handoff was overwriting shared files. Duplicate process tree rooted at PID 3207335 is paused; do not resume it into this worktree.
