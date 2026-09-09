# HANDOFF 7 → Codex — fix the independent final audit findings, then re-run the release gate

Branch v2-foundation. Same ground rules (read-only OCI; generic repo; every doc number reproducible; pytest + linters green per commit;
CODEX-STATUS.md at the end — and DELETE all skills/*/CODEX-STATUS.md handoff notes from the tree, they must not ship).
Findings (32, with file:line evidence and proposed fixes) are in docs/final-audit-findings.json — read every entry. Fix ALL critical,
high and medium; fix the low ones that are cheap (most are). Order and grouping, one commit each:

1. GUARD (critical+high): scripts/guard_lib.py — (a) danger-flag branch must never downgrade: compute the leaf tier FIRST, then `--force`/danger
   flags can only raise (allow→ask, ask→deny), never lower; (b) a command with no decision must NOT return permissionDecision "allow" — return
   no decision (let Claude Code's own permission system apply) — an explicit allow is only for leaves classified read; (c) the opaque-shell
   regex must not match `.sh` script paths (`foo.sh --flag`), anchor it to a shell binary token; (d) V8 test must not be self-confirming:
   classify_leaf must be measured against research/data/destructive-ops.json severity labels (independent of catalog_rules READ_PREFIX),
   publish the resulting matrix; (e) README/foundation wording "unknown commands ask" → state exactly what asks, what is passed through.
   Add tests for each of a–d including the 25 bypass strings the auditor used (see findings evidence).
2. SANITIZER (medium+low): scripts/lib/sanitize.py — collapse newlines to a single space separator (not delete); fix the flag name; extend
   detection for the 3 missed novel strings in the findings; drop the 2 false positives on ordinary resource names; tests.
3. SKILL SCRIPTS (high+medium): cert_expiry.py --limit 20 (+ guard at :13); triage.py and scripts/lib/oci_ro.py flag saturation when
   rows == --limit (thread limit through); check_scripts_readonly.py must verify scripts actually CALL oci_ro (AST/import+call), not substring;
   add a live smoke that RUNS every skill script (tenancy-scoped) to the V25 sweep and record results; fix the two scripts that import
   oci_ro without routing through it.
4. CONTENT (medium+low): the 22 thin skills — every skills/<s>/references/*.md must carry at least one fenced verified command or a table
   with error strings (use the research files named in plan §3.2 as source; no invention); Route 'Why' column must be real routing text
   (no 'Load when needed.' boilerplate) in all 33; Scope check must name only variables the skill's fences use; fix the malformed sentence
   in oci-bastion-access/SKILL.md:82; remove `allowed-tools` script globs from the 6 no-script skills; make lint_fences require --query on
   every read fence (DoD 6.1.1) and fix fences accordingly; route the infra/ops skills to references/service-command-cards.md per ERRATA N11.
5. PLUGIN/INSTALL (high+medium+low): .claude-plugin/plugin.json must declare mcpServers (the bundled server) so `claude --plugin-dir` registers
   the 15 tools; install.sh must exclude skills/*/CODEX-STATUS.md (they are deleted anyway) and must `uv sync --frozen` in the TARGET runtime
   (or document the first-call install explicitly); oci-readonly-smoke --live must read region from the profile when --region is absent;
   README install sequence corrected.
6. CLAIMS (high+medium+low): regenerate catalog (inventory.py --scripts --examples) so V11/V14/V16 truly pass; release_gate.py must write to
   a scratch path and DIFF against the tracked docs (never overwrite silently); check_history.py must actually scan history for real OCIDs
   (ocid1.<type>.oc1.<realm>.<20+chars>), emails, key blocks; docs/evals.md and tests/test_evals.py must reference evals/corpus/eval-corpus.json
   (not research/); docs/routing-model-eval.md must point to evals/routing-judge-prompt.md and only the existing scorer path; README line 5
   and 69 must describe the real test status; V27 reason updated to the actual `claude plugin eval` output at HEAD; always-resident floor:
   publish BOTH the raw chars/4 figure and a measured host-framing figure (measure with `claude --plugin-dir` + /context or the per-skill
   framing template the auditor used), label the method.
7. RELEASE GATE: re-run the full §6.2 matrix via release_gate.py, commit the diffed docs/validation-matrix.md with real results; final
   CODEX-STATUS.md at repo root only, listing anything still red with owner.
