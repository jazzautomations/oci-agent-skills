# Signing and scanning gates
Source: research/09a §§9–10.
OCI image signing binds an image digest to a KMS asymmetric signing key/version and a signing algorithm supported by both services. An AES encryption key is not a signing key. Keep private key operations in KMS and scope sign/verify permission separately.
Check signature validity, trusted key identity and the digest selected for deployment. A tag-only verification can race with a retag.
Container scanning and Application Dependency Management audits cover different inputs: an image/package finding is not the same as an application dependency graph finding. A stage that starts an audit must wait for its terminal result and enforce the chosen severity/exception policy.
No signing, scan creation or audit stages were run in this tenancy. [unverified] Exact scanner JSON, repository scan schedules and build-run integration require current installed schema and service configuration checks before a runnable proposal.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| RelatedResourceNotAuthorizedOrNotFound | An OCID **inside the request body** (subnet, image, vault key, NSG) is missing or unreadable by you | id 7 [unverified] |
| NotAuthenticated | Signature/key/clock/region-subscription problem — see §6 | id 9 [unverified] |
