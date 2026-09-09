# Landing zones, CIS and organizations
Source: research/13 §3.2 and §5.1, research/09c B2; asset status verified by `gh api`
2026-09-08. This is the single most stale-prone area in any OCI answer — restate the dates.

## Asset status
| Asset | Status |
|---|---|
| `oci-landing-zones/terraform-oci-core-landingzone` — *the* current tenancy baseline | ALIVE, release v1.6.0 (2026-06-08), pushed 2026-09-01, CIS OCI Foundations Benchmark v3.0 |
| `oci-landing-zones/oci-cis-landingzone-quickstart` | Terraform config **RETIRED May 2025** (frozen at 2.8.8); the repo lives on as the CIS **Compliance Script**, release v3.4.1 (2026-08-14) |
| `oci-landing-zones/oci-landing-zone-operating-entities` | ALIVE — the multi-entity / business-unit model |
| `oci-landing-zones/oracle-enterprise-landingzone` (OELZ v2) | dormant, last push 2025-03-04 |
| `oci-landing-zones/oci-scca-landingzone` (US Gov SCCA) | pushed 2026-03-16 |
| `terraform-oci-modules-{networking,iam,security,governance,observability,workloads,oracle-database,orchestrator}` | ALIVE, most pushed within five weeks of the snapshot |
| `oracle-devrel/terraform-oci-arch-*` (85 repos) | FROZEN — all last pushed 2025-01-21 or earlier; `terraform-oci-arch-web-ha` is archived |

Rule: cite an `arch-*` stack as a worked example or diagram source; cite `oci-landing-zones/*`
as something to actually run. Never call an `arch-*` stack "current".

## The four things to say before proposing a landing zone
1. **Free tier breaks CIS.** Cloud Guard and Security Zones do not exist in free-tier
   tenancies, so a free-tier landing zone is CIS-non-compliant by construction.
2. **An active ZPR Security Attribute Namespace blocks `terraform destroy`** until retired.
3. **Offer the Resource Manager one-click, not a local apply.** The stack writes
   root-compartment policies, i.e. tenancy-admin blast radius; the RM URL hands the operation
   to a human in their own console and the agent never holds those credentials. Form:
   `https://cloud.oracle.com/resourcemanager/stacks/create?zipUrl=https://github.com/oci-landing-zones/terraform-oci-core-landingzone/archive/refs/heads/main.zip`
4. **"Are we CIS compliant?" has a read-only answer.** `scripts/cis_reports.py` in the CIS
   quickstart repo (release v3.4.1) is the only CIS-compliance evidence generator an agent may
   run unattended. Do **not** enumerate CIS control numbers from memory — Oracle's docs do not
   carry them, and the benchmark text is published by CIS. Its section breakdown (IAM,
   Networking, Logging and Monitoring, Object Storage, Asset Management, with Level 1/Level 2
   profiles) is `[unverified]` — asserted by secondary sources, not read from CIS.

## Stale URLs
`cloud-adoption-framework/landing-zone-v1.htm`, `…/implementation-landing-zone-v2.htm` and
`…/cis-benchmark-landing-zone.htm` all now 302 to a single `…/technology-implementation.htm`.
Deep-linking them still "works" and silently lands elsewhere. The CAF pages that still resolve
to themselves are `oci-landing-zones-overview.htm` and `oci-core-landing-zone.htm`. The
Architecture Center slug `cis-oci-benchmark/` now describes Core Landing Zone, not the retired
stack: enclosing compartment, Network/Security/App/Database compartments, standalone or
hub-and-spoke or DMZ VCN topologies, with Cloud Guard, VCN flow logs, Connector Hub, Vault
with customer-managed keys, VSS, Security Zones and ZPR pre-wired.

Partner appliances: the `deploy-partners-to-cis-lz/` page still describes the retired base
LZ — say so, then point at Core LZ, which offers OCI Network Firewall or a partner appliance
natively.

## Organizations and child tenancies
`oci organizations` carries `organization`, `organization-tenancy`, `child-tenancy`,
`sender-invitation` / `recipient-invitation` (the cross-tenancy join handshake),
`subscription` / `assigned-subscription` / `subscription-mapping` (how a child draws on the
parent's Universal Credits), `link`, `domain` / `domain-governance` and `governance`.
Cross-tenancy *policy* enforcement is a separate group,
`oci governance-rules-control-plane governance-rule`, which pushes quota, tag and Cloud Guard
rules from parent down into child tenancies. Both `organizations organization list` and
`governance-rule governance-rule list` ran live 2026-09-09; the governance-rule leaf declares
no required flag in the CLI yet returns `MissingParameter` (400) without `--compartment-id`.

Docs: https://docs.oracle.com/en-us/iaas/Content/General/organization/home.htm — the widely
cited `General/Concepts/organization_management_overview.htm` now **301s** here (checked
2026-09-09); cite the destination, not the redirect ·
CAF: https://docs.oracle.com/en-us/iaas/Content/cloud-adoption-framework/home.htm

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| NotAuthorizedOrNotFound | Deliberate ambiguity: missing resource OR missing policy OR wrong region OR wrong compartment | id 13 [unverified] |
| NoEtagMatch | Optimistic-concurrency `if-match` stale | id 23 [unverified] |
