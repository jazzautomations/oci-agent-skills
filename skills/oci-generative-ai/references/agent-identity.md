# Agent identity and model IAM

Separate human caller, host resource principal, managed agent service principal and each tool's downstream database/API identity. Confirm compartment and tenancy boundaries for each hop. Never solve a denial by granting manage all-resources.
Model discovery permission does not imply permission to invoke. The target.model.id condition can restrict supported chat, embedding and rerank inference; it is not a blanket restriction on model-management resources. Verify the current IAM reference before proposing policy text.
An endpoint OCID is a routing identifier, not a credential. Do not place signing keys, API keys, saved DB credentials or user access tokens in prompts, tool schemas or logs. Use approved secret delivery and preserve caller authorization across retrieval and tools.
