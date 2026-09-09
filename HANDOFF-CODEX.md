# HANDOFF → Codex (gpt-6-astra) — Wave 0/1 foundation of oci-agent-skills v2

You are building the FOUNDATION layer of v2 on branch `v2-foundation`. Another engine is
simultaneously writing research (only under `research/`, gitignored) and the v2.1 skill plan.
You do NOT touch `research/`, `skills/`, `docs/` (except a new docs/foundation.md) or `README.md`.
You DO own: `scripts/`, `hooks/`, `catalog/`, `runtime/`, `tests/`, `.github/`, `installers/`.

## Ground rules (non-negotiable)
- OCI: CLI 3.91 installed, profile DEFAULT, region us-chicago-1, a REAL tenancy. ONLY read-only
  operations (list/get/search/head/summarize/--help). NEVER create/update/delete/start/stop anything.
- Repo is GENERIC and publishable: no tenancy OCIDs, no personal names/use cases, no secrets in git.
- Keep the honesty discipline audited in research/A3-audit-codex-claims.md: every number you write in
  docs must be reproducible by a command you also ship. No "verified" without the command that verifies.
- Commit per work package with a clear message. Run `uv run --frozen --project runtime pytest -q tests`
  green before each commit. Write progress to `CODEX-STATUS.md` (done / next exact step) after each package.
- Read first: research/00-SYNTHESIS-AND-V2-PLAN.md §2.5 (guard), §2.6 (MCP), §2.7 (catalog), §3 (W01-W07),
  research/A2-audit-codex-mcp-runtime.md, research/A4-audit-codex-catalog.md, research/05-surface-reverse-engineering.md
  §6 (guard spec), research/data/guard-hook-regex-v2.json, research/data/destructive-ops.json, research/data/cli-leaves.json.

## Coordinator decisions that OVERRIDE the plan where they differ
- D3 Scripts are read-only by construction. Every OCI call from any plugin script goes through ONE
  wrapper: `scripts/lib/oci_ro.sh` and `scripts/lib/oci_ro.py` (same allowlist: leaf verbs
  list|get|search|head|summarize|describe|generate-*-json-input|--help, plus an explicit allowlist of
  read-only leaves from catalog that don't match those verbs, e.g. `os ns get`, `limits resource-availability get`).
  Anything else → exit 3 with a one-line reason. Scripts never mutate.
- D3b The PreToolUse hook also matches Bash commands that invoke `${CLAUDE_PLUGIN_ROOT}/scripts/...` and applies
  the same allowlist to their argv.
- D4 Guard tiers: `--profile <anything>` and `--auth <anything>` are ALLOW (not ask). Keep ASK for
  `--force`, bulk-delete*, `--empty-bucket*`, `terraform apply/destroy/state rm`, `-auto-approve`,
  `kubectl delete/drain`, `drop|remove` SQL/APEX admin calls. Publish the confusion matrix ONLY for the
  measured oci-leaf classifier (replay all 9,145 leaves in tests); label non-oci rules as unmeasured hand rules.
- D5 MCP: grow 9 → 14 read-only tools (oci_whoami, oci_work_requests, oci_alarm_status, oci_audit_events,
  oci_metrics with fixed MQL templates, oci_price_lookup via the public price API); fix the two production
  defects (lru_cached auth that never refreshes a session token → TTL/mtime + 401 invalidate-and-retry;
  sync tools blocking the event loop → async def + anyio.to_thread); prefix/subtree compartment allowlist;
  `compartment_depth` on the cost tool; token counts in docs marked as estimates.
- D8 NO symlinks anywhere. Shared references will live in `references/` at repo root (another engine
  writes their content); your installer (`installers/install.sh --target <dir>`) COPIES, never links.
- Catalog v2 (from A4): replace the 3.1 MB single-line catalog/cli.json with `catalog/cli.jsonl`
  (one leaf per line, pretty fields: path, short_help, kind, verb, required params, has_dry_run,
  has_wait_for_state, has_all, severity from destructive-ops), `catalog/cli-read.jsonl` (read-only subset),
  `catalog/index.json` (one row per root service: name, op count, read/mutating/destructive counts, one-line
  purpose), and `scripts/catalog.py {find,help,severity,service}` that answers a query in ≤400 tokens of
  output. Keep `scripts/inventory.py` as the generator (add `--format jsonl --index`). Delete the old cli.json.

## Work packages (in order; each = one commit)
W01 Catalog v2 (above) + tests/test_catalog.py.
W02 Guard hook: `scripts/guard_oci.py` (stdin JSON PreToolUse payload → permissionDecision allow/ask/deny
    JSON on stdout, exit 2 for deny), `scripts/guard_lib.py` (parser: split on ; && || |, handle sudo/env
    prefixes, quotes, `oci` anywhere in the segment, xargs), `scripts/redact.py` (OCIDs/keys/tokens in
    hook messages), `hooks/hooks.json` (PreToolUse matcher Bash), `catalog/guard.json` (final rules),
    `tests/test_guard.py` replaying all 9,145 leaves + 60 hand-written shell forms + 20 bypass attempts
    (base64, eval, python -c "import oci", printf | sh). Print the confusion matrix from the test.
W03 (SKIP — content, not yours)
W04 Template + CI validators: `skills/_TEMPLATE/SKILL.md` (per plan §2.3 house template; sections:
    Scope check / Route / Commands / Failure modes / Hard rules), `scripts/ci/check_frontmatter.py`
    (name, description ≤400 chars containing "Use when" and "Not for"), `scripts/ci/check_refs.py`
    (every relative link resolves, no ../../docs), `scripts/ci/lint_fences.py` (every fenced `oci ...`
    line: leaf exists in catalog, required params present, --all or --limit on list ops; verify against
    `oci ... --help` when `--live-help` flag), `scripts/ci/check_no_secrets.py`, `.github/workflows/validate.yml`
    (pins OCI CLI 3.91.0 via pip in CI). Run all validators on the current 16 skills and report.
W05 MCP defect fixes (D5) + tests for token expiry, concurrent tools/call, subtree allowlist.
W06 MCP tools 10–14 (D5) + smoke entries + offline tests; live smoke read-only against DEFAULT profile.
W07 (SKIP manifests — depend on final skill set) EXCEPT: `installers/install.sh --target <dir>` that copies
    the plugin for Codex/Gemini/Cursor/opencode hosts, and `.mcp.json` updated for the 14-tool server.
Finally: `docs/foundation.md` describing each shipped mechanism with the exact command that verifies it,
and the unowned-services list (services with zero read-only allowlist entries) from catalog/index.json.
