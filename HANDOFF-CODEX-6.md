# HANDOFF 6 → Codex — Wave 3: regenerate, package, evals, head-to-head, docs, final gate

Branch v2-foundation. Same ground rules (read-only OCI; generic, publishable repo; every number in docs reproducible by a shipped
command; pytest + all linters green before each commit; CODEX-STATUS.md after each package). Read research/00-PLAN-V2.1.md §5 Wave 3
(W42–W46), §6 (definition of done, validation matrix, unowned services) and research/00-PLAN-V2.1-ERRATA.md (B1 W42a, B2 W08b, N1, N5, N6, N9).
By now all 33 v2 skills exist and are committed (batches A, B, C). Packages, one commit each:

1. Cleanup v1: delete the 13 v1 skill dirs that have no v2 successor (oci-ai-data, oci-compute-network, oci-devops, oci-finops, oci-iac,
   oci-identity, oci-observability, oci-reliability, oci-sdk, oci-security, oci-storage, oracle-database, oracle-multicloud-enterprise)
   and their catalog/fragments/*.json and any baseline entries in catalog/validation-baseline.json that referenced them. Remove the
   legacy baseline exemptions so the strict content gates apply to the 33 v2 skills for real; fix whatever fails.
2. W42a Regenerate: `scripts/inventory.py --scripts --examples` → catalog/scripts.json (sha256 of every plugin script), merge
   catalog/fragments/*.json → catalog/examples.json, re-sign catalog/guard.json; update the installer's fixed skill count; the two
   currently failing tests must pass; two regenerations byte-identical.
3. W42 Live validation: `scripts/check_examples.py --live --profile DEFAULT --region us-chicago-1` on the D7-scoped subset; record
   sanitized results in docs/validation-cli.json; everything else marked shape-only. No relabelling failures as empty.
4. W08b: populate marketplace.json `skills[]` (33 / db subset / devops subset per plan §2.2), `claude plugin validate . --strict` and
   `claude plugin validate ./skills --strict` pass; `find . -type l` empty in the distributed tree; installers/install.sh copies the
   33 skills + references/ + hooks + .mcp.json.
5. W43 Evals: import research/data/eval-corpus.json (80 routing prompts, 40 negatives N01–N40, 40 task cases, 10 safety strings from
   references/untrusted-output.md classes) into evals/ in BOTH shapes the plan §2.8 names (case.yaml for `claude plugin eval` and the
   skill-creator shape); write the routing/negative/safety/command-validity graders; ship `scripts/eval/run.py` that can run the
   routing + negative + command-validity + safety arms offline (description matching + lint_fences + guard replay) and prints the
   §6.2 metrics (V19 routing ≥0.9, V20 negatives 0/40 hard gate). Run it; record results in docs/evals.md. If `claude plugin eval`
   is available locally, run it too and record; if not, say so.
6. W44 Head-to-head: same offline corpus run in four arms — this pack / research/refs/adibirzu_oci-skills / research/refs/oracle_mcp
   (oci-api + oci-cloud tool descriptions as the "skills") / bare — using research/17 §5 fairness rules; metrics: routing accuracy,
   false-positive rate, fenced-command validity via lint_fences, mutation-without-confirm via guard replay, always-resident tokens.
   Write docs/head-to-head.md with the table and the exact command that reproduces it.
7. W45 Docs: rewrite README.md (install for Claude Code / Codex / Gemini / Cursor / opencode, what's inside, safety model with the
   real guard matrix + Oracle denylist comparison from research/data/denylist-coverage.json, MCP 15 tools, token floor per ERRATA N1,
   verification section with reproducible commands, boundaries, "not affiliated with Oracle" trademark paragraph per plan §2.10),
   docs/audit.md (provenance matrix: what came from which research/community repo; unowned services §6.3 with op counts),
   docs/install.md, docs/mcp-optional.md, CHANGELOG.md, LICENSE check (check_licenses.py green). Keep the A3 honesty discipline.
8. W46 Final gate: run the entire §6.2 validation matrix; write docs/validation-matrix.md with one row per gate: command, result,
   date. Every red row must say why and who owns it. Do NOT merge to main; leave the branch ready and write the final CODEX-STATUS.md.
