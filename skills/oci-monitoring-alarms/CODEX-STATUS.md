# oci-monitoring-alarms status

Completed 2026-09-09 on v2-foundation. Sources read: `09b` §1–4, §9–12, `11` §4. Template §4.1, library §4.2 and B1/B3/N3/N4 applied.

Checks: all seven handoff linters pass; LICENSE.txt matches the root Apache-2.0 license; lint_fences used --live-help. Fragment leaf/required flags/read policy/JMESPath checks and script --help pass. 2 failed, 199 passed, 1 warning in 65.64s (0:01:05).

Live evidence: [{"example": "oci-monitoring-alarms-1", "ok": true, "count": 20, "scope": "bounded sample"}]. No mutations executed; mutation fences and rollback are proposals only. Metadata separates partial reads from shape-only operations.

Documentation HTTP checks: [{"url": "https://docs.oracle.com/en-us/iaas/Content/Monitoring/Concepts/monitoringoverview.htm", "status": 200}, {"url": "https://docs.oracle.com/en-us/iaas/Content/Monitoring/Reference/mql.htm", "status": 200}, {"url": "https://docs.oracle.com/en-us/iaas/Content/Monitoring/Tasks/managingalarms.htm", "status": 200}].

Full-suite integration gate: 2 failed, 199 passed, 1 warning in 65.64s (0:01:05). Deferred only: tests/test_catalog.py::test_generated_scripts_and_fragments, tests/test_installer.py::test_installed_copies_and_refs. The fixed legacy 16-skill count and generated registry expectations require edits outside this handoff; all other tests pass.

Limits: list evidence is bounded and not a tenancy inventory. Unavailable resources have no behavioral verification. Shared references and generated catalog integration belong to other owners; W42a must regenerate registries. The current example live runner has a narrower placeholder/flag allowlist than these fragments, so custom scoped wrapper checks supply live evidence. This status is inside the assigned directory because root CODEX-STATUS.md is outside the permitted write scope.

Additional offline checks passed: zero series and empty datapoints block review; a real datapoint with value zero is accepted; malformed/non-finite values and invalid or over-24-hour windows are rejected. Mocked main-path calls were checked against the read-only wrapper policy. No alarm was created.

## Handoff 3 completion record

All eleven assigned skills are implemented in the requested commit order on v2-foundation. All required §3.2 reference files, named helpers, exact routing descriptions, path selectors and Apache-2.0 licenses are present. Each skill has a read-command fragment and dated validation JSON. No tenancy mutation, Terraform execution, function invocation, alarm creation or notification publication was performed.

| Skill/status | Commit | Seven linters | Live service evidence |
|---|---|---|---|
| [oci-compute](../oci-compute/CODEX-STATUS.md) | 2d61ec4 | 7/7 pass | oci-compute-1: passed, 3 rows, oci-compute-2: passed, 9 rows, oci-compute-3: passed, 1 rows, oci-compute-4: passed, 1 rows |
| [oci-networking](../oci-networking/CODEX-STATUS.md) | 323d6ed | 7/7 pass | oci-networking-1: passed, 6 rows, oci-networking-2: passed, 6 rows, oci-networking-3: passed, 0 rows |
| [oci-object-storage](../oci-object-storage/CODEX-STATUS.md) | e537118 | 7/7 pass | oci-object-storage-1: passed, 1 rows, oci-object-storage-2: passed, 1 rows |
| [oci-block-file-storage](../oci-block-file-storage/CODEX-STATUS.md) | 6f514d4 | 7/7 pass | shape-only; no service resources exercised |
| [oci-bastion-access](../oci-bastion-access/CODEX-STATUS.md) | 8fe550f | 7/7 pass | shape-only; no service resources exercised |
| [oci-oke](../oci-oke/CODEX-STATUS.md) | c8f4bc8 | 7/7 pass | shape-only; no service resources exercised |
| [oci-devops-pipelines](../oci-devops-pipelines/CODEX-STATUS.md) | e24bbdb | 7/7 pass | shape-only; no service resources exercised |
| [oci-serverless](../oci-serverless/CODEX-STATUS.md) | be04170 | 7/7 pass | shape-only; no service resources exercised |
| [oci-terraform](../oci-terraform/CODEX-STATUS.md) | bf855d5 | 7/7 pass | shape-only; no service resources exercised |
| [oci-vault-certificates](../oci-vault-certificates/CODEX-STATUS.md) | a3aff82 | 7/7 pass | oci-vault-certificates-1: passed, 0 rows |
| [oci-monitoring-alarms](CODEX-STATUS.md) | this commit | 7/7 pass | oci-monitoring-alarms-1: passed, 20 rows |

There are 64 read examples across the eleven fragments. All 33 primary documentation links returned HTTP 200. CLI leaf/required flags, JMESPath syntax, wrapper read policy, script help and executable shell syntax were checked. Mutation commands were checked with help only and include rollback proposals.

Additional behavior checks cover rule-array merge validation, block/boot attachment correlation and incomplete samples, both Terraform replacement orders and sensitive-value omission, certificate date boundaries and missing dates, and MQL zero-datapoint/malformed-response refusal. The Terraform discovery snapshot preserves all 132 research rows byte-for-byte.

### Requirements that cannot be completed within this handoff

The requested fully green pytest gate is not achieved: every full run has 199 passing tests and exactly two integration failures. tests/test_catalog.py::test_generated_scripts_and_fragments requires regenerating shared catalog registries; tests/test_installer.py::test_installed_copies_and_refs hardcodes 16 skills. Catalog generation belongs to W42a, and the test edits are outside these assigned directories. Both failures are recorded rather than hidden. Early scoped reruns deselected only those two tests and passed all 199 remaining tests.

The current live-example runner does not accept all placeholders/flags used by these fragments. Scoped calls through oci_ro and explicit fragment validation supplied evidence instead; runner/registry integration remains with W42a. Shared references are produced by other owners and were not edited here.

Physical Compute capacity cannot be established with the wrapper-approved reads: capacity_probe.sh reports limits, not host placement. No resources were created to broaden verification. The remaining operation-specific limits are in each skill status and its [unverified] references; a successful empty or bounded list never proves tenancy-wide absence or mutating behavior.

Root CODEX-STATUS.md was not written because the user explicitly restricted writes to assigned skill directories and fragment files. This consolidated record and the eleven per-skill CODEX-STATUS.md files satisfy reporting within that boundary.
