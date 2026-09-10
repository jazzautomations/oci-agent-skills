# Agent identity and model IAM

Separate human caller, host resource principal, managed agent service principal and each tool's downstream database/API identity. Confirm compartment and tenancy boundaries for each hop. Never solve a denial by granting manage all-resources.
The [managed API-calling tool](https://docs.oracle.com/en-us/iaas/Content/generative-ai-agents/api-calling-tool-guidelines.htm)
can use resource-principal authentication for OCI APIs, with the required IAM
authorization. An [ADK local function](https://docs.oracle.com/en-us/iaas/Content/generative-ai-agents/adk/api-reference/quickstart.htm)
runs in its host process; its downstream credentials come from that execution
environment. Do not assume that the managed agent's principal signs every local
SDK call. Ask which execution path is in use when the request does not say.
Model discovery permission does not imply permission to invoke. The target.model.id condition can restrict supported chat, embedding and rerank inference; it is not a blanket restriction on model-management resources. Verify the current IAM reference before proposing policy text.
An endpoint OCID is a routing identifier, not a credential. Do not place signing keys, API keys, saved DB credentials or user access tokens in prompts, tool schemas or logs. Use approved secret delivery and preserve caller authorization across retrieval and tools.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| SignUpRequired | Service not enabled for the tenancy (common on Gen-AI, some ADB features) | id 12 [unverified] |
| InvalidParameter | A body/query parameter value is invalid or malformed | id 2 [unverified] |
