# HANDOFF 5 → Codex — finish Wave 2 batch A (11 skills built by the other engine; you apply the fixes)

Branch v2-foundation. Same ground rules (read-only OCI, generic repo, linters + pytest green before each commit, CODEX-STATUS.md).
Skills: oci-navigator, oci-cli-auth, oci-tenancy-governance, oci-iam-policy, oci-support-limits, oci-logging-audit,
oci-incident-triage, oci-security-posture, oci-cost-analysis, oci-free-tier, oci-sdk-patterns (all exist under skills/, uncommitted,
with catalog/fragments/<name>.json). Adversarial verifier findings for 8 of them are in research/lote-A-verifier-findings.json
(oci-security-posture, oci-free-tier, oci-sdk-patterns have NO verifier report: verify them yourself with the same 10 checks:
linters, --help of every fenced command, description byte-equal to research/00-PLAN-V2.1.md §3.2 row, no invented claims vs source
research, scripts read-only via scripts/lib/oci_ro, no OCIDs/secrets, token budget §2.9, "# MUTATING —" + rollback on mutating fences,
stencil sections, dead links).
For each skill: apply every finding, run all linters (scripts/ci/*.py per docs/foundation.md) + the tenancy-scoped live reads,
fix until green, commit one by one (skill dir + its fragment). Finish with CODEX-STATUS.md.
