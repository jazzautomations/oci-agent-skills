# HANDOFF 12 → Codex — Migration Copilot: skills `oci-migration-assess`, `oci-migration-map`, `oci-migration-landing-zone` + demo

Branch main. Ground rules as always (read-only OCI; no AWS/GCP/Azure credentials exist here — everything for source clouds runs on the
synthetic fixture or --help; never invent CLI flags: verify with the locally installed aws/gcloud/az if present, else cite docs and
tag [unverified]). Commit per item, push at the end, CODEX-STATUS.md.
INPUTS: research/19-migration-copilot.md, research/24-migration-real-problems.md (25 blockers, 10 questions an assessment must
answer, archetypes), research/25-migration-deep-study.md (inventory commands per cloud, sizing translation tables, price APIs with
real responses, LZ inputs, Cloud Migrations/Cloud Bridge/ZDM matrix, fixture), research/28-oci-vs-aws-azure-gcp-2026.md (pricing +
parity matrix), research/29-real-migration-stories.md (what to warn BEFORE moving), references/architecture-center.md.
DELIVER:
1. skills/oci-migration-assess: SKILL.md + references/inventory-{aws,gcp,azure}.md (read-only commands + minimal IAM policy each,
   verified or [unverified]) + scripts/inventory_normalize.py (source-cloud CLI JSON → common inventory schema; schema in
   references/inventory-schema.json) + fixtures/aws-sample.json (the 12-resource synthetic stack from 25). No cloud credentials needed
   to run on the fixture.
2. skills/oci-migration-map: SKILL.md + references/service-map.md (~40 rows, sourced) + references/sizing.md (instance→shape,
   EBS→VPU, RDS→ADB/BaseDB) + references/warnings.md (the blockers from 24/29 as pre-move warnings with triggers) + scripts/map_and_price.py
   (inventory → OCI target list + monthly cost comparison using OCI price API (live) and the source cloud price where a public API
   exists (AWS bulk/Query, Azure retail: live curl; GCP: [unverified] if key needed) → JSON + markdown report with the 10 questions
   from 24 answered or marked "needs customer input").
3. skills/oci-migration-landing-zone: SKILL.md + references/landing-zone-inputs.md (CIS LZ / Core LZ variables that the inventory
   can fill) + scripts/emit_tfvars.py (inventory → tfvars + compartment/VCN plan) + the Resource Manager stack creation commands
   (# MUTATING, never executed) + rollback.
4. demos/migration-copilot/: README + `make demo` (or run.sh) that runs the three scripts on the fixture and produces
   report.md (redacted, generic) — this is what gets shown. Save the produced report to docs/evidence/migration-sample-report.md.
5. fragments, tests (fixture-driven, golden files), catalog regen, docs/skills.md regen, docs/migration.md, README row. All validators green.
