# Resource discovery
Source: research/08c §5; research/data/tf-rd-services.json.
tf-rd-services.json is a byte-for-byte snapshot of the 132 service/scope rows collected in research. Count rows, not unique service names: some names appear for both tenancy and compartment scope. It is not proof that every resource in a service is supported.
Choose an explicit region, compartment and service filter. Resource discovery can read broad tenancy data and emit HCL/state containing identifiers and secrets. Keep generated artifacts local and redacted; do not publish them.
Generated code needs provider/version review, reference cleanup, naming, dependency checks and a no-change plan before adoption. Discovery itself is not an import or a safe apply plan. [unverified] No discovery provider execution, plan or apply was performed here.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| `404-NotAuthorizedOrNotFound` right after a `oci_identity_compartment` create | New compartment OCID used immediately by dependent resources; IAM is eventually consistent across regions | id 91 [unverified] |
| `404-NotAuthorizedOrNotFound` but "the resource was created" | Provider's post-create read runs against a different region/compartment, or the service principal lacks read policy | id 92 [unverified] |
