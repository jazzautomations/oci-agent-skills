# oracle-apex — handoff 4

Completed. No tenancy mutations executed.

- The five CLI blocks inspect ADB hosting metadata, not APEX application functionality. SQLcl, SQL and browser validation need a separately supplied target and remain unverified.

- Full pytest: 2 failed, 199 passed, 1 warning in 73.38s (0:01:13). Two protected integration gates fail: catalog regeneration (deferred to W42a) and the stale 16-skill installer assertion. They cannot be fixed within assigned ownership; the scoped regression run excludes only those two.
- All seven handoff linters passed, including live CLI help; git diff --check passed.
- Pytest: 199 passed, 2 deselected, 1 warning in 71.53s (0:01:11).
- All 3 Oracle documentation URLs returned HTTP 200 on 2026-09-09.
- Permitted tenancy smoke reads: identity passed, subscriptions passed, compartment passed, shapes passed, images passed, availability-domains passed, network passed, namespace passed, vaults passed, monitoring passed. These do not validate this skill's domain operations.
- Domain CLI shapes verified; SQL, provisioning and billable operations remain unexecuted.
- Evidence: validation-evidence.json. W42a fragment merge/script registry regeneration belongs to the coordinator; generated catalogs were not edited.
