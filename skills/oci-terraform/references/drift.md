# Drift handling
Source: research/08c §9; research/14 §10.
Compare the declared configuration, selected state and remote resource. Distinguish intentional emergency changes from provider normalization and unauthorized drift.
A Resource Manager drift detection operation creates job/service state and is outside this repository's read-only contract. Read existing job metadata first; propose detection explicitly when needed. A refresh-only apply still changes state.
Do not automatically reconcile drift: applying old code may remove a deliberate emergency fix or recreate data resources. Choose whether configuration or remote reality becomes authoritative, record that decision and review a new plan.
For 404 immediately after IAM compartment creation, verify region and dependency ordering and allow bounded propagation. Do not insert an unconditional sleep as a substitute for identifying the missing permission or resource.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| `404-NotAuthorizedOrNotFound` right after a `oci_identity_compartment` create | New compartment OCID used immediately by dependent resources; IAM is eventually consistent across regions | id 91 [unverified] |
| `404-NotAuthorizedOrNotFound` but "the resource was created" | Provider's post-create read runs against a different region/compartment, or the service principal lacks read policy | id 92 [unverified] |
