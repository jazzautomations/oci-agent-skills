# CI identity choices
Source: research/09a §11; shared auth-modes.
| Runner | Identity to investigate | Constraint |
|---|---|---|
| OCI DevOps managed build | Project resource principal | Project dynamic group/policy |
| Self-hosted OCI Compute | Instance principal | Runner instance dynamic group; IMDS access |
| External GitHub runner | API signing key in protected secrets | Least privilege and key rotation |
| Supported external federation | Documented federation flow | Confirm OCI feature and audience/subject constraints |
Never assume AWS-style GitHub OIDC role exchange exists in OCI. [unverified] Research's external OIDC workflow was not executed; validate the exact supported identity-domain flow before offering it.
Use protected environments and branch rules for deployment secrets. Pin third-party actions to reviewed revisions. Pull-request code must not receive deployment credentials. Do not copy a developer's personal ~/.oci directory into an image.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| RelatedResourceNotAuthorizedOrNotFound | An OCID **inside the request body** (subnet, image, vault key, NSG) is missing or unreadable by you | id 7 [unverified] |
| NotAuthenticated | Signature/key/clock/region-subscription problem — see §6 | id 9 [unverified] |
