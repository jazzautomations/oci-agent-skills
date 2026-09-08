# Foundation progress

Done on `v2-foundation`:

- W01: deterministic JSONL inventory, strict read subset, service index, bounded query helper and catalog tests.
- W02: advisory Bash hook, redaction, shared read-only execution wrappers, full leaf replay and shell/opaque-form fixtures. Variable option values preserve read classification; opaque segments cannot downgrade a known denial.
- W04: house template, frontmatter/reference/fence/secret validators and CLI-pinned CI. Existing skill content is unchanged. The explicit legacy baseline contains 16 description-routing findings and 25 prohibited cross-doc links; new findings and stale exemptions fail CI.
- W05: TTL/mtime auth refresh, one retry after 401, concurrent worker dispatch, verified ancestor/subtree restrictions, cost scope/depth, bounded names and full pytest discovery. Subcompartment subtree reads use bounded tenancy discovery and exclude sibling branches.
- W06: all six requested additions, fixed response projections, offline tests and live smoke. `oci_limits` consolidates the old limit tools to retain a fourteen-tool surface. Public pricing handles both localization schemas and absent SKUs.
- Installer and documentation: copy-only installation for Codex, Gemini CLI, Cursor and OpenCode v2, updated `.mcp.json`, host launcher tests and `docs/foundation.md` with exact verification commands and the unowned-services list.

Validation completed:

- `uv run --frozen --project runtime pytest -q tests`: **165 passed**; one upstream Authlib deprecation warning.
- `uv run --no-project --with oci-cli==3.91.0 python scripts/inventory.py --format jsonl --index --check`: byte-identical, no import errors.
- `uv run --frozen --project runtime oci-readonly-smoke`: fourteen tools, estimated schema size 3,461 tokens (characters / 4, rounded up).
- `OCI_CONFIG_PROFILE=DEFAULT uv run --frozen --project runtime oci-readonly-smoke --live --region us-chicago-1`: all 18 checks passed; no tenancy mutation commands were run.
- Frontmatter and reference validators pass with the explicitly recorded legacy baseline. Installed live-help fence validation, tracked secret/symlink scan, Ruff and whitespace checks pass.
- All generated host MCP launch commands pass stdio discovery from an unrelated working directory and an installation path containing spaces. No interactive host UI pickup is claimed.

Next exact step: none for the requested foundation scope. W03 content and W07 marketplace/manifests remain intentionally outside this handoff; current skill baseline findings belong to the content work packages.

Environment note: a duplicate process executing this identical handoff was overwriting shared files. Its process tree rooted at PID 3207335 remains paused to preserve state and prevent further writes. Inspect with `ps -o pid,stat,args -p 3207335`; do not resume it into this completed worktree.
