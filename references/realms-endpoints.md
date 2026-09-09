Purpose: realms, region counts, endpoints and gov/sovereign differences.
Source: research/16-oracle-runtimes-email-compliance.md §C, research/data/regions-endpoints.json, research/data/regions.json; generated 2026-09-08; verified-on CLI 3.91.0

## 1. Realms and second-level domains

**20 realms, 85 known regions**, from Python SDK 2.185.0 [verified].

Realm → second-level domain (region count): `oc1` oraclecloud.com (46) · `oc2`
oraclegovcloud.com (2) · `oc3` oraclegovcloud.com (3) · `oc4` oraclegovcloud.uk (2) ·
`oc19` oraclecloud.eu (2) · `oc8` (2) · `oc9` (2) · `oc10` (1) · `oc14` (6) · `oc15` (1) ·
`oc20` (1) · `oc21` (2) · `oc23` (2) · `oc24` (2) · `oc26` (2) · `oc29` (2) · `oc35` (3) ·
`oc42` (2) · `oc51` (1) · `oc52` (1) — unnamed ones are `oraclecloud<N>.com` [verified].

The 44 keys `oci iam region list` returns are 3 letters (`FRA`, `IAD`); region **ids** are the
full form (`eu-frankfurt-1`). **Dedicated Region** ids and keys are "not available in public
documentation, check with your Oracle contact" [verified]; **OCI Alloy** is absent from the SDK realm table [verified by
absence]. Both: unknown realm, no assumption.

## 2. Three region counts — never interchangeable

| Number | What it is | How to get it |
|---|---|---|
| **44** | regions this oc1 tenancy could subscribe to [verified] | `oci iam region list` |
| **46** | regions the SDK knows in realm `oc1` [verified] | SDK region table |
| **85** | regions the SDK knows across all 20 realms [verified] | SDK region table |
| fewer | regions subscribed now [verified] | `oci iam region-subscription list` |

`oci iam region list` answers "regions **my realm** offers", not "regions Oracle operates";
the CLI's `--region` help under-states that [verified on 3.91.0]. Doc: "You can't access
regions that aren't in your realm" [verified].

## 3. Never string-build an endpoint

**165 of the 170 SDK endpoint templates carry `{secondLevelDomain}`**, supplied by the realm [verified]: 130 plain `https://<svc>.{region}.oci.{secondLevelDomain}` + 24 other `.oci.`
variants + 9 `.ocp.` + 2 `.ocs.` (`network_firewall`, `service_manager_proxy`). Of those 24:
12 carry `{dualStack?ds.:}` (renders plain when off), `core`/`object_storage` carry
`{dualStack?ds.oci.:}` (drops `oci` when off), 10 have no `.oci.` label (`audit`, `database`,
`identity_data_plane`). The 5 without `{secondLevelDomain}` are hardcoded: `identity_domains`
(per-tenancy IDCS host — read the domain object's `url`; `oci iam domain list --url` [verified
on CLI 3.91.0]) and four `osub_*` (`csaap-e.oracle.com`).

- Pass `--region <id>`, let the CLI/SDK resolve the host; a concatenated
  `oraclecloud.com` cannot resolve in oc2/oc3/oc4/oc19.
- `--realm-specific-endpoint` selects the realm-scoped form (env
  `OCI_REALM_SPECIFIC_SERVICE_ENDPOINT_TEMPLATE_ENABLED`) [verified on 3.91.0]; `--endpoint`
  overrides the default service endpoint / API version path — use only a host a service
  returned.
- Console links are oc1-shaped: outside oc1, suppress (`references/console-links.md`).

## 4. Government and sovereign realms

| Cloud | Realm | Domain | Note |
|---|---|---|---|
| US Government (FedRAMP) / US Defense (DoD) | `oc2` / `oc3` | oraclegovcloud.com | two separate realms [verified] |
| UK Sovereign | `oc4` | oraclegovcloud.uk | separate realm [verified] |
| EU Sovereign | `oc19` | oraclecloud.eu | `eu-frankfurt-2`, `eu-madrid-2`; "completely isolated both physically and logically from other Oracle realms" [unverified — search summary; realm/domain pair *is* verified from the SDK] |
| Australia Gov & Defence | — | — | own doc page [verified as a link on regions.htm] |

**Expect service absence, not just a different host.** These realms carry an
authorized-services subset: a `ServiceNotFound` or DNS failure is a legitimate "not offered
here" (§6, rule 3).

## 5. Compliance artifacts are Console-only

"Compliance Documents does not have public API, SDK, or CLI support at this time" — Console
path **Identity & Security → Compliance**; types Attestation (PCI DSS AoC), Audit, Bridge
Letter, Certificate, SOC3, Other; present in US Gov, US Defense and UK Sovereign too
[verified]. No `oci compliance` group exists in 3.91.0 [verified]. Public page:
https://www.oracle.com/corporate/cloud-compliance/ [unverified — not fetched].

**Name collision.** `get_compliance`, `list_compliance_policies`/`-records`,
`generate_compliance_report` are **Fleet Application Management** (`oci
fleet-apps-management`) — *patch* compliance of your own fleet, not Oracle's attestations
[verified]. Asked for "the SOC 2 report": no command exists; give the Console path.

## 6. Agent rules

1. Read the config/region realm; never assume `oc1`.
2. Build no URLs — endpoints, Console links or docs (§3).
3. Gov/sovereign service absence is an answer, not a retry (§4).
4. Never copy an OCID, tenancy name or region key across realms.

## Docs

All HTTP 200 on 2026-09-08.

- Regions/realms — https://docs.oracle.com/en-us/iaas/Content/General/Concepts/regions.htm
- Compliance Documents — https://docs.oracle.com/en-us/iaas/Content/ComplianceDocuments/Concepts/compliancedocsoverview.htm
- EU Sovereign — https://docs.oracle.com/en-us/iaas/Content/sovereign-cloud/eu-sovereign-cloud.htm
- US Gov / Defense / AU Gov — https://docs.oracle.com/en-us/iaas/Content/gov-cloud/govfedramp.htm · `…/govfeddod.htm` · `…/ausgov.htm`
- UK Sovereign — https://docs.oracle.com/en-us/iaas/Content/uk-sovereign-cloud/home.htm (`govuksouth.htm` 301s here)
