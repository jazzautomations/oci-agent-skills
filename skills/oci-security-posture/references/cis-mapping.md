# CIS mapping and the audit report

Verified 2026-09-09 against OCI CLI 3.91.0, `us-chicago-1`.

## The benchmark
Research snapshot: **CIS Oracle Cloud Infrastructure Foundations Benchmark v3.0.0**, published by CIS
(cisecurity.org), not by Oracle. Sections: Identity and Access Management, Networking, Logging
and Monitoring, Object Storage, Asset Management. Each recommendation carries a Level 1 or
Level 2 profile `[unverified — secondary sources, not re-read from CIS]`.

**Never enumerate control numbers from memory.** Cite the benchmark itself, or run the
CIS Compliance Script (`cis_reports.py`, release v3.4.1 / 2026-08-14) from
`oci-landing-zones/oci-cis-landingzone-quickstart`; review its pinned source and read-only scope before running it.
State the version you used next to any "CIS-compliant" claim.

## Landing-zone reality (2026-09-08 evidence)
* `oci-landing-zones/terraform-oci-core-landingzone` — the current tenancy baseline, release
  v1.6.0 (2026-06-08), CIS v3.0. This is what "CIS landing zone" means today.
* `oci-cis-landingzone-quickstart` — the **Terraform config was retired May 2025** (frozen at
  2.8.8); the repo now ships the compliance script only.
* `oracle-enterprise-landingzone` (OELZ v2) — dormant since 2025-03-04. Do not recommend it.
* Oracle's `cloud-adoption-framework` landing-zone pages (v1, v2, cis-benchmark) all **302 to
  one `technology-implementation.htm`**; deep links to the old page names are dead.

**Free-tier caveat, state it before proposing a landing zone:** Cloud Guard and Security Zones
do not exist in a free-tier tenancy, so record unavailable controls as gaps against the chosen benchmark; do not infer
overall compliance from account type alone.

## What this skill can actually evidence
Report as: severity · resource · evidence command · fix (proposed, never run).

| Check | Sev | Evidence command (read-only) | Fix belongs to |
|---|---|---|---|
| user without MFA | HIGH | `iam user list` + `is-mfa-activated` | Console/identity domain |
| API key older than 90 days | MED | `iam user api-key list` + `time-created` | user rotates, then delete |
| `any-user` / `manage all-resources` policy | HIGH | `iam policy list` + `statements` | `oci-iam-policy` |
| public bucket | CRIT | `os bucket get` + `public-access-type` | `oci-object-storage` |
| bucket without a customer-managed key | MED | `os bucket get` + `kms-key-id` is null | `oci-vault-certificates` |
| `0.0.0.0/0` ingress to 22 or 3389 | CRIT | `network security-list list` ingress rules | `oci-networking` |
| `0.0.0.0/0` ingress to any other port | HIGH | same fence | `oci-networking` |
| Cloud Guard not enabled | HIGH | `cloud-guard configuration get` 404 | tenancy admin, one-time |
| no VSS target on compute | MED | `vulnerability-scanning host scan target list` | `oci-compute` |

Verb, variable and condition semantics for judging a policy statement live in the shared
`references/iam-variables.md` at the repo root — read it before calling a policy over-broad.

## Two checks with no CLI at all
* **Oracle's own attestations** (SOC 2/3, PCI AoC, ISO, bridge letters) are **Console-only**:
  Identity & Security -> Compliance. No `oci compliance` group exists in 3.91.0 `[verified]`.
  The SDK's `list_compliance_records` / `get_compliance` belong to Fleet Application
  Management (patch compliance of your own fleet) — a different question entirely.
* **Password and sign-on policy** for an identity domain is read through the domains API,
  not classic IAM; depth here is a named gap `[unverified]`.

## Reporting rules
1. Name the scope: profile, region(s), compartment OCIDs read, and the timestamp.
2. Redact before writing: full OCIDs, user names, IPs, key fingerprints, bucket names.
3. Separate "found" from "not checked". A disabled service, an unread compartment, an
   unsubscribed region and a missing permission all render as zero findings.
4. Attach the exact command per finding so a human can reproduce it.
5. Propose the fix as text with its rollback. This skill never mutates.

Docs: https://docs.oracle.com/en-us/iaas/Content/ComplianceDocuments/Concepts/compliancedocsoverview.htm
· https://www.cisecurity.org/benchmark/oracle_cloud
