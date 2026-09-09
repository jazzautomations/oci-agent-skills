# Model availability

Discover in the user's subscribed region, using list_models.sh or the bounded command in SKILL.md. Return id, capabilities and time-deprecated; do not pin example model IDs or reuse historical model counts. A bounded page is incomplete: page deliberately or authorize --all locally through OCI_RO_ALLOW_ALL=1.
Select a currently supported capability and serving mode before building a request. Preserve unknown model/vendor enum values. A published regional table describes availability, not tenant entitlement or capacity. Separate authorization failure from a valid empty response. Model retirement requires revalidation of output quality, context/token limits and costs; never silently substitute a vendor.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| SignUpRequired | Service not enabled for the tenancy (common on Gen-AI, some ADB features) | id 12 [unverified] |
| InvalidParameter | A body/query parameter value is invalid or malformed | id 2 [unverified] |
