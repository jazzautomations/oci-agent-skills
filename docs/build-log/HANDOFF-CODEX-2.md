# HANDOFF 2 → Codex — close the Wave 0/1 gaps between your foundation and PLAN v2.1

Branch `v2-foundation` (your 6 commits are the baseline). Same ground rules as HANDOFF-CODEX.md
(read-only OCI only, generic repo, reproducible claims, pytest green before each commit, CODEX-STATUS.md after each package).
You own: scripts/, hooks/, catalog/, runtime/, tests/, .github/, installers/, .claude-plugin/, .codex-plugin/, .mcp.json,
docs/install.md, docs/mcp-optional.md, docs/foundation.md, skills/_TEMPLATE/. You do NOT touch references/ (another
engine is writing it right now), skills/<real skills>/, research/, README.md.

READ FIRST: research/00-PLAN-V2.1.md §2 (architecture), §4.1 (template, verbatim), §4.2 (scripts/lib contracts), §5 Wave 0 + Wave 1
(W01–W08 deliverables and done-when), §6.2 (validation matrix); then research/00-PLAN-V2.1-ERRATA.md (overrides).
Then diff each W01–W08 done-when against what you shipped (docs/foundation.md) and close every gap. Known gaps:

1. scripts/lib/sanitize.py per §4.2 + research/15 §8 (untrusted-output cleaner: delimiters, control-char strip, codepoint truncation, flags; idempotent) + tests/test_sanitize.py with the research/15 §9 strings (must be flagged AND still returned).
2. scripts/console_url.py per research/12 B2–B5 (OCID → cloud.oracle.com URL; never console.<region>.oraclecloud.com) + tests/test_console_url.py.
3. catalog/scripts.json (sha256 per plugin script) generator `inventory.py --scripts`, guard rule for `${CLAUDE_PLUGIN_ROOT}/...` script invocations (unknown/sha-mismatch ⇒ ask; argv checked with the oci_ro allowlist), and `inventory.py --examples` merging `catalog/fragments/*.json` into catalog/examples.json (ERRATA B1). Guard non-oci rules (terraform/kubectl/SQL/APEX per §2.5) present and labelled unmeasured; `--profile`/`--auth` ALLOW (D4). Confusion matrix printed by tests over all 9,145 leaves.
4. Missing CI linters: scripts/ci/{check_portable,check_links,check_budget,check_scripts_readonly,check_licenses}.py per W05; `.github/workflows/{cli-drift,links-nightly}.yml`. check_refs.py exempts non-.md files (ERRATA B3). check_frontmatter enforces description ≤400 chars containing "Use when:" and "Not for:", and `metadata.verified ∈ {live, partial, shape-only}` (ERRATA N3). Empirically settle the `paths` frontmatter behaviour (ERRATA N2) and record the finding in docs/foundation.md.
5. skills/_TEMPLATE/SKILL.md must be byte-equal to plan §4.1 (sections Scope check / Route / Commands / Failure modes / Hard rules), citing references/error-corpus.json.
6. MCP: provenance envelope `{source, trust, complete}` replacing content_note/scope_note (W07); tool count statement per ERRATA N5; schema token estimate labelled as estimate; no imperative aimed at the model inside results.
7. W08a: .claude-plugin/plugin.json + marketplace.json with 3 entries (oci-agent-skills, -db, -devops) WITHOUT skills[] yet, all with hooks; .codex-plugin/plugin.json; docs/install.md; docs/mcp-optional.md (Oracle oci-api on-demand with warning; oci-cloud = skip and why); install.sh exits non-zero for an unguarded host without --i-accept-unguarded; `find . -type l` empty.
8. Update docs/foundation.md: every mechanism + the exact verify command; note the W42a regeneration step.
Commit per numbered item. Finish with CODEX-STATUS.md listing any W01–W08 done-when you could NOT satisfy and why.
