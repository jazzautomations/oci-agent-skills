# Foundation progress

- W01 done: JSONL catalog, strict read subset, service index, bounded query helper and catalog tests. Inventory scope and import errors live in `catalog/cli-meta.json` and `catalog/index.json`.
- Validation: `uv run --frozen --project runtime pytest -q tests` — 47 passed. Two generator runs produced byte-identical CLI artifacts (CLI 3.91.0).
- W02 done: Bash advisory guard, redaction, shared shell/Python read-only execution wrapper, catalog replay, 60 shell forms and 20 opaque-form tests. Non-OCI rules are explicitly unmeasured.
- W02 validation: full suite passed (135 tests including W04 validator fixtures); leaf matrix is recorded in `catalog/guard.json`.
- W04 done: house template, metadata/reference/fence/secret validators and CLI-pinned CI. All fenced commands passed installed live-help validation.
- Current skill report: 16 routing-description violations and 25 cross-doc links are recorded in `catalog/validation-baseline.json`; existing skill content remains untouched. Strict validators report these findings; CI accepts only the exact baseline, including removal of stale exemptions. The new template passes without exemptions.
- Next exact step: finish W05 auth/concurrency/subtree/cost regression tests and commit runtime fixes.
- Tool count decision: consolidate limit discovery and values into one MCP tool so all six requested additions fit the fourteen-tool surface.
- Environment: duplicate execution of this identical handoff was overwriting shared files. Duplicate process tree rooted at PID 3207335 is paused; do not resume it into this worktree.
