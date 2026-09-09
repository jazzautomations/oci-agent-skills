# Projects and pipelines
Source: research/09a §§4–6.
A project requires a Notifications configuration, including a reviewed topicId. Creating a project without it fails validation. Keep source connection, build pipeline, build stages, output artifacts, deployment pipeline, environment and approval stage distinct.
Resolve stage predecessor IDs to form an acyclic graph. Build output alone does not establish that an artifact was delivered or deployed. Inspect the specific build run or deployment and its stage state before bounded logs.
OCI DevOps projects use a resource principal. Give the project identity only the artifact, secret, target-environment and log permissions required by its stages. User permissions to create a pipeline do not authorize the running pipeline.
An approval stage belongs before the material deployment action; it is not a substitute for reviewing the proposed change. Trigger filters should constrain repository, branch and event. Preserve previous artifact digests and rollout configuration for rollback.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| RelatedResourceNotAuthorizedOrNotFound | An OCID **inside the request body** (subnet, image, vault key, NSG) is missing or unreadable by you | id 7 [unverified] |
| NotAuthenticated | Signature/key/clock/region-subscription problem — see §6 | id 9 [unverified] |
