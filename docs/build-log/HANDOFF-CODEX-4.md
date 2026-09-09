# HANDOFF 4 → Codex — Wave 2 batch B: 11 skills (database, AI, DR, enterprise)

Branch `v2-foundation`. Ground rules as before (read-only OCI, generic repo, reproducible claims, pytest + all linters
green before each commit, CODEX-STATUS.md after each skill). Two other engines are writing OTHER skills and references/
right now: you own ONLY these directories: skills/<name>/ for the 11 names below, and catalog/fragments/<name>.json.
Do not edit references/, catalog/* (other than fragments/), scripts/, runtime/, docs/, README, or any other skill.

Skills (one commit each, in this order):
oracle-autonomous-db, oracle-db-fleet, oracle-db-vector-ai, oracle-db-sql-access, oracle-apex, oci-generative-ai,
oci-ai-services, oci-data-platform, oci-dr-backup, oci-migration-patching, oracle-enterprise-apps

For EACH skill:
1. Read its row in research/00-PLAN-V2.1.md §3.2 (name, description text, paths, mode R/M, outline, references, scripts,
   source research files, live?), §4.1 template (skills/_TEMPLATE/SKILL.md is the byte-exact stencil), §4.2 lib contracts,
   research/00-PLAN-V2.1-ERRATA.md (B1 fragments, B3 error-corpus path, N3 verified enum, N4 no-script line),
   and the source research files named in the row (read them fully; they contain the verified commands).
2. Write skills/<name>/SKILL.md following the stencil: frontmatter (name, description ≤400 chars with "Use when:" and
   "Not for:" exactly as in the row, paths if the row has it, metadata.verified ∈ live|partial|shape-only), sections
   Scope check / Route / Commands / Failure modes / Hard rules. Commands = 5-10 RUNNABLE fenced `oci ...` blocks with every
   required flag, a --query projection, --limit or --all on list ops; mutating fences carry `# MUTATING —` prefix and a
   rollback line. Failure modes cite ids from references/error-corpus.json. Hard rules include the untrusted-output
   paragraph by reference to references/untrusted-output.md. Links to shared references are relative (../../references/x.md).
3. Write skills/<name>/references/*.md (skill-specific, per the row) and skills/<name>/scripts/* (read-only, every OCI call
   through scripts/lib/oci_ro; if the row says no script, add the ERRATA N4 line instead).
4. Write catalog/fragments/<name>.json: example rows (same schema as catalog/examples.json) for every read command in the skill.
5. Run: scripts/ci/check_frontmatter.py, check_refs.py, check_portable.py, lint_fences.py --live-help, check_budget.py,
   check_no_secrets.py, check_scripts_readonly.py on the skill; run the read-only commands that this tenancy can exercise
   (compute shapes/images/AD, network, object storage namespace, vault list, monitoring metadata) and record the outcome in
   the skill's Failure modes footer as the plan's live/partial/shape-only evidence. Fix until green. Commit.
Finish with CODEX-STATUS.md: per skill, linter results, live evidence, and any §3.2 requirement you could not satisfy and why.

Extra (allowed for this handoff only): trim references/jmespath.md to ≤4780 bytes and references/realms-endpoints.md to ≤5560 bytes
by removing redundant wording only (no facts, tags, URLs or rows removed); commit as its own change.
Another engine is building oci-support-limits, oci-logging-audit, oci-incident-triage, oci-security-posture, oci-cost-analysis,
oci-free-tier, oci-sdk-patterns concurrently — never touch those directories.
