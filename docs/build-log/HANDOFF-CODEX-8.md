# HANDOFF 8 → Codex — last fixes, then merge v2-foundation into main (no push)

Same ground rules. Read-only OCI. One commit per item, then the merge.
1. V25 script sweep must supply scope: derive PROFILE=DEFAULT, REGION (profile region), TENANCY_ID and COMPARTMENT_ID (=tenancy root),
   INSTANCE_ID (first instance in root, or skip instance-scoped scripts with status "skipped: no instance"), and for validate_mql a fixed
   probe (METRIC_NAMESPACE=oci_computeagent, MQL='CpuUtilization[1m].mean()', last hour). Re-run the sweep, re-record docs/validation-scripts.json.
   A script that returns ok:false because the tenancy has no data is a GAP, not a script failure — record status "ran, gap" distinct from "failed".
2. skills/oci-monitoring-alarms/scripts/validate_mql.py: an empty summarize result (CLI prints nothing) must yield {"ok":false,"kind":"no_datapoints",...},
   not "failed_or_malformed_read". Same audit for every other skill script that treats empty stdout as malformed (scripts/lib/oci_ro should
   return ok:true, data:[] for empty stdout on list/summarize ops — tests).
3. scripts/ci/check_history.py: git author/committer emails and Co-Authored-By/Claude-Session trailers are NOT leaks (exempt); only emails/OCIDs/keys
   inside patch bodies count. Report the exact blobs still carrying an email (docs/final-audit-findings.json in commits 85815c5/a320700) and
   write docs/history-purge.md with the exact `git filter-repo --replace-text` (or filter-branch) command to purge them BEFORE the first push,
   plus how to rewrite the author identity if the owner chooses to. Do not rewrite history yourself.
4. Re-run release_gate.py, commit the diffed docs/validation-matrix.md. Then: `git checkout main && git merge --no-ff v2-foundation` with a
   merge message summarizing v2 (33 skills, 15 MCP tools, guard, 16 references, evals), run pytest + strict validators on main, and write the
   final CODEX-STATUS.md on main. Do NOT push anywhere.
