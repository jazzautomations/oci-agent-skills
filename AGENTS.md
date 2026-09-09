# Repository work

Read the active handoff and research plan/errata before changing package scope. Research is build-only and does not ship. Preserve source provenance and explicit unverified claims.

OCI validation is read-only: use bounded, explicitly scoped reads through scripts/lib/oci_ro; never provision, change IAM, run generic executor tools or execute mutation fixtures. Never print or commit tenancy identifiers, credentials, account data or raw service errors. Mutation examples are inert and must have a shape-only marker and rollback guidance.

Regenerate catalog/scripts.json, examples.json and guard.json with scripts/inventory.py --scripts --examples after script/fragment changes. Run pytest and strict scripts/ci validators before commits; no baseline exemptions. Record red evaluation/release gates honestly with an owner. Keep package commits on the user's named branch; do not merge to main unless explicitly requested.

Use the copy installer to inspect the distributed tree. It excludes research, environments, the authoring stencil and handoff scratch files. Skills, scripts, shared references and runtime must remain portable together. The pre-existing local auth-modes edit and Autonomous Database handoff scratch files are user work; do not discard them.
