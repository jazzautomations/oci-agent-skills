# Foundation progress

- W01 done: JSONL catalog, strict read subset, service index, bounded query helper and catalog tests. Inventory scope and import errors live in `catalog/cli-meta.json` and `catalog/index.json`.
- Validation: `uv run --frozen --project runtime pytest -q tests` — 47 passed. Two generator runs produced byte-identical CLI artifacts (CLI 3.91.0).
- W02 done: Bash advisory guard, redaction, shared shell/Python read-only execution wrapper, catalog replay, 60 shell forms and 20 opaque-form tests. Non-OCI rules are explicitly unmeasured.
- W02 validation: full suite passed (135 tests including W04 validator fixtures); leaf matrix is recorded in `catalog/guard.json`.
- W04 done: house template, metadata/reference/fence/secret validators and CLI-pinned CI. All fenced commands passed installed live-help validation.
- Current skill report: 16 routing-description violations and 25 cross-doc links are recorded in `catalog/validation-baseline.json`; existing skill content remains untouched. Strict validators report these findings; CI accepts only the exact baseline, including removal of stale exemptions. The new template passes without exemptions.
- W05 done: auth cache TTL and credential-file mtime invalidation, single retry after 401, async worker dispatch, ancestry-checked subtree allowlists, explicit cost descendant/region scope and compartment depth, bounded untrusted resource names, full pytest discovery.
- W05 validation: `uv run --frozen --project runtime pytest -q tests` — 142 passed, including concurrent real MCP stdio calls and offline token-expiry/scope tests.
- W06 done: all six new diagnostic/pricing tools, consolidated `oci_limits`, fixed field projections, smoke entries and offline coverage.
- W06 validation: live smoke against DEFAULT/us-chicago-1 passed all 18 checks; reports fourteen tools and a schema estimate of 3,461 tokens. Current combined suite passed 160 tests. Public prices handle both documented and observed localization fields and null results for absent SKUs.
- Next exact step: finish copy-only installer checks, document reproducible foundation mechanisms and limitations, run all final checks, then commit installer and documentation.
- Tool count decision: consolidate limit discovery and values into one MCP tool so all six requested additions fit the fourteen-tool surface.
- Environment: duplicate execution of this identical handoff was overwriting shared files. Duplicate process tree rooted at PID 3207335 is paused; do not resume it into this worktree.
