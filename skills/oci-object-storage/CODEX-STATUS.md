# oci-object-storage status

Completed 2026-09-09 on v2-foundation. Sources read: `04c` Object Storage, `09b` §29, `14` §8, `15` §2 (Tier-0 object names). Template §4.1, library §4.2 and B1/B3/N3/N4 applied.

Checks: all seven handoff linters pass; LICENSE.txt matches the root Apache-2.0 license; lint_fences used --live-help. Fragment leaf/required flags/read policy/JMESPath checks and script --help pass. 199 passed, 2 deselected, 1 warning in 132.85s (0:02:12).

Live evidence: [{"example": "oci-object-storage-1", "ok": true, "count": 1, "scope": "single resource or unpaginated metadata"}, {"example": "oci-object-storage-2", "ok": true, "count": 1, "scope": "bounded sample"}]. No mutations executed; mutation fences and rollback are proposals only. Metadata separates partial reads from shape-only operations.

Documentation HTTP checks: [{"url": "https://docs.oracle.com/en-us/iaas/Content/Object/Concepts/objectstorageoverview.htm", "status": 200}, {"url": "https://docs.oracle.com/en-us/iaas/Content/Object/Tasks/usingpreauthenticatedrequests.htm", "status": 200}, {"url": "https://docs.oracle.com/en-us/iaas/Content/Object/Tasks/usinglifecyclepolicies.htm", "status": 200}].

Full-suite integration gate: 2 failed, 199 passed, 1 warning in 66.58s (0:01:06). Deferred only: tests/test_catalog.py::test_generated_scripts_and_fragments, tests/test_installer.py::test_installed_copies_and_refs. The fixed legacy 16-skill count and generated registry expectations require edits outside this handoff; all other tests pass.

Limits: list evidence is bounded and not a tenancy inventory. Unavailable resources have no behavioral verification. Shared references and generated catalog integration belong to other owners; W42a must regenerate registries. The current example live runner has a narrower placeholder/flag allowlist than these fragments, so custom scoped wrapper checks supply live evidence. This status is inside the assigned directory because root CODEX-STATUS.md is outside the permitted write scope.
