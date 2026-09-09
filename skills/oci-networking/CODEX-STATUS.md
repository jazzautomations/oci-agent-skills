# oci-networking status

Completed 2026-09-09 on v2-foundation. Sources read: `04c` Networking/LB, `09b` §16–19, `13` §5.2. Template §4.1, library §4.2 and B1/B3/N3/N4 applied.

Checks: all seven handoff linters pass; LICENSE.txt matches the root Apache-2.0 license; lint_fences used --live-help. Fragment leaf/required flags/read policy/JMESPath checks and script --help pass. 199 passed, 2 deselected, 1 warning in 31.44s.

Live evidence: [{"example": "oci-networking-1", "ok": true, "count": 6, "scope": "bounded sample"}, {"example": "oci-networking-2", "ok": true, "count": 6, "scope": "bounded sample"}, {"example": "oci-networking-3", "ok": true, "count": 0, "scope": "bounded sample"}]. No mutations executed; mutation fences and rollback are proposals only. Metadata separates partial reads from shape-only operations.

Documentation HTTP checks: [{"url": "https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/overview.htm", "status": 200}, {"url": "https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/networksecuritygroups.htm", "status": 200}, {"url": "https://docs.oracle.com/en/solutions/hub-spoke-network-drg/index.html", "status": 200}].

Full-suite integration gate: 2 failed, 199 passed, 1 warning in 30.95s. Deferred only: tests/test_catalog.py::test_generated_scripts_and_fragments, tests/test_installer.py::test_installed_copies_and_refs. The fixed legacy 16-skill count and generated registry expectations require edits outside this handoff; all other tests pass.

Limits: list evidence is bounded and not a tenancy inventory. Unavailable resources have no behavioral verification. Shared references and generated catalog integration belong to other owners; W42a must regenerate registries. The current example live runner has a narrower placeholder/flag allowlist than these fragments, so custom scoped wrapper checks supply live evidence. This status is inside the assigned directory because root CODEX-STATUS.md is outside the permitted write scope.
