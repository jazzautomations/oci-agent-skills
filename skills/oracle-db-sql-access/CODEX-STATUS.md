# oracle-db-sql-access — handoff 4

Completed. No tenancy mutations executed.

- Handoff requires read-only scripts: readonly_user.sql audits an existing user instead of creating one; negative_test.sql reports risk instead of attempting DML/DDL. Setup and actual denial testing are documented for a separately authorized isolated database. Read-only enforcement is not certified.
- Plan description is 377 characters; shortened scope sentence to meet 400, retaining Use when/Not for text verbatim.

- Full pytest: 2 failed, 199 passed, 1 warning in 27.63s. Two protected integration gates fail: catalog regeneration (deferred to W42a) and the stale 16-skill installer assertion. They cannot be fixed within assigned ownership; the scoped regression run excludes only those two.
- All seven handoff linters passed, including live CLI help; git diff --check passed.
- Pytest: 199 passed, 2 deselected, 1 warning in 31.50s.
- All 3 Oracle documentation URLs returned HTTP 200 on 2026-09-09.
- Permitted tenancy smoke reads: identity passed, subscriptions passed, compartment passed, shapes passed, images passed, availability-domains passed, network passed, namespace passed, vaults passed, monitoring passed. These do not validate this skill's domain operations.
- Domain CLI shapes verified; SQL, provisioning and billable operations remain unexecuted.
- Evidence: validation-evidence.json. W42a fragment merge/script registry regeneration belongs to the coordinator; generated catalogs were not edited.
