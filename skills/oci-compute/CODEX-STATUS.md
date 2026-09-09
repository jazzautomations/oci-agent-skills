# oci-compute status

Completed 2026-09-09 on v2-foundation. Sources read: `04c` Compute, `06c`, `14` §4. Template §4.1, library §4.2 and B1/B3/N3/N4 applied.

Checks: all seven handoff linters pass; LICENSE.txt matches the root Apache-2.0 license; lint_fences used --live-help. Fragment leaf/required flags/read policy/JMESPath checks and script --help pass. 199 passed, 2 deselected, 1 warning in 33.30s.

Live evidence: [{"example": "oci-compute-1", "ok": true, "count": 3, "scope": "single resource or unpaginated metadata"}, {"example": "oci-compute-2", "ok": true, "count": 9, "scope": "bounded sample"}, {"example": "oci-compute-3", "ok": true, "count": 1, "scope": "bounded sample"}, {"example": "oci-compute-4", "ok": true, "count": 1, "scope": "bounded sample"}]. No mutations executed; mutation fences and rollback are proposals only. Metadata separates partial reads from shape-only operations.

Documentation HTTP checks: [{"url": "https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/launchinginstance.htm", "status": 200}, {"url": "https://docs.oracle.com/en-us/iaas/Content/Compute/References/computeshapes.htm", "status": 200}, {"url": "https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/troubleshooting-out-of-host-capacity.htm", "status": 200}].

Full-suite integration gate: 2 failed, 199 passed, 1 warning in 34.92s. Deferred only: tests/test_catalog.py::test_generated_scripts_and_fragments, tests/test_installer.py::test_installed_copies_and_refs. The fixed legacy 16-skill count and generated registry expectations require edits outside this handoff; all other tests pass.

Limits: list evidence is bounded and not a tenancy inventory. Unavailable resources have no behavioral verification. Shared references and generated catalog integration belong to other owners; W42a must regenerate registries. The current example live runner has a narrower placeholder/flag allowlist than these fragments, so custom scoped wrapper checks supply live evidence. This status is inside the assigned directory because root CODEX-STATUS.md is outside the permitted write scope.

capacity_probe.sh reports limit availability, not physical hosts: create-compute-capacity-report is outside the wrapper read-only contract. Physical placement remains unknown.
