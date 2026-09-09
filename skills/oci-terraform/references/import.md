# Import without accidental replacement
Source: research/08c §4.
Inventory the resource's region, compartment and existing state ownership. Do not import one OCI resource into multiple active states. Back up state securely and prevent concurrent writers before a state change.
An import maps an existing remote object to an address; it does not infer complete desired configuration. Write matching configuration and inspect the next plan. Unspecified immutable properties can cause replacement immediately after import.
Use the import identifier documented for that exact resource type; many need composite identifiers rather than a bare OCID. Import blocks and moved blocks improve reviewability when supported by the chosen Terraform/OpenTofu version.
Import, state mv/rm/push and backend migration mutate state and are proposals only. Never use state rm as a deletion workaround without an explicit ownership transfer and recovery plan.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| `404-NotAuthorizedOrNotFound` right after a `oci_identity_compartment` create | New compartment OCID used immediately by dependent resources; IAM is eventually consistent across regions | id 91 [unverified] |
| `404-NotAuthorizedOrNotFound` but "the resource was created" | Provider's post-create read runs against a different region/compartment, or the service principal lacks read policy | id 92 [unverified] |
