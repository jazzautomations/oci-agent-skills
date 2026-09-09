# Compartment design
Source: research/09c B1, research/13 §5.1; verified-on OCI CLI 3.91.0, 2026-09-09.

The compartment is the blast-radius, IAM, quota and budget boundary at once. A hierarchy
that does not match the cost-ownership model makes budgets and quotas meaningless.

## Rules that hold up in real tenancies
- **Never build in the root compartment.** Create one *enclosing* compartment per landing
  zone so the environment can be re-created, moved or handed over without touching tenancy
  root. The OCI Core Landing Zone exposes this as an explicit option.
- **Segment by job function first, environment second.** The reference split is
  Network / Security / Application Development / Database (+ optional Exadata
  Infrastructure), each with its own admin group, reflecting how IT responsibility is
  actually split. Environment (dev/test/prod) nests inside, or becomes a separate top-level
  branch when isolation must be absolute.
- **Keep hierarchies shallow.** Policy-statement limits apply per compartment hierarchy,
  and the CIS landing-zone compliance checker audits exactly that (IAM-18/IAM-19).
- **Quotas and budgets target compartments.** Both `oci limits quota` and `oci budgets`
  take a compartment, so design the tree around who pays before who deploys.
- **Deletion is slow and asynchronous.** The landing-zone authors default to *not*
  destroying compartments on `terraform destroy` because they "may take a long time to
  delete". Never offer compartment deletion as a rollback step.

## Reading the tree honestly
`--compartment-id-in-subtree true` walks the whole subtree; `--access-level ANY` includes
compartments you can only partially see, so the count is the *visible* tree, not the tenancy
truth. Executed live in the reference tenancy 2026-09-09: three ACTIVE compartments under
root. An empty or short result is evidence about your permissions as much as about the
tenancy — say which.

Sub-compartment usage counts toward the parent for quota purposes, and a compartment OCID is
region-independent while the resources inside it are not.

## Mutations that belong on a destructive review path
`oci iam compartment` also exposes `move`, `recover`, `bulk-move-resources` and
`bulk-delete-resources`. The last two are compartment-wide mutations: propose them only with
an explicit inventory of what they will touch, and never as part of a cleanup sweep.

## Routing a design question
| The user says… | Move |
|---|---|
| "compartment structure", "segregation of duties" | Propose enclosing + Network/Security/App/Database (+Exadata). Name the enclosing compartment explicitly; the module family is `terraform-oci-modules-iam`. |
| "multiple business units", "child tenancies" | Core Landing Zone is a single-entity model. The multi-entity model is `oci-landing-zones/oci-landing-zone-operating-entities`. |
| "US Gov", "SCCA", "FedRAMP-shaped" | `oci-landing-zones/oci-scca-landingzone` — different realm, different console hostnames. |
| "ransomware", "immutable backups", "isolated recovery" | Architecture Center slug `oci-tenancy-cyber-resilience-architecture/` (created 2026-08-03). |

Docs: https://docs.oracle.com/en-us/iaas/Content/Identity/compartments/managingcompartments.htm ·
policy limits per hierarchy: https://docs.oracle.com/en-us/iaas/Content/Identity/policymgmt/policy-limits-compartment-hierarchy.htm

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| NotAuthorizedOrNotFound | Deliberate ambiguity: missing resource OR missing policy OR wrong region OR wrong compartment | id 13 [unverified] |
| NoEtagMatch | Optimistic-concurrency `if-match` stale | id 23 [unverified] |
