# Import without accidental replacement
Source: research/08c §4.
Inventory the resource's region, compartment and existing state ownership. Do not import one OCI resource into multiple active states. Back up state securely and prevent concurrent writers before a state change.
An import maps an existing remote object to an address; it does not infer complete desired configuration. Write matching configuration and inspect the next plan. Unspecified immutable properties can cause replacement immediately after import.
Use the import identifier documented for that exact resource type; many need composite identifiers rather than a bare OCID. Import blocks and moved blocks improve reviewability when supported by the chosen Terraform/OpenTofu version.
Import, state mv/rm/push and backend migration mutate state and are proposals only. Never use state rm as a deletion workaround without an explicit ownership transfer and recovery plan.
