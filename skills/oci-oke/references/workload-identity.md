# Workload identity
Source: research/09a §18.
Workload identity is scoped by cluster, namespace and service account, and requires an enhanced cluster. It is distinct from node instance principals and from image-pull credentials. Dynamic groups are not the workload identity mechanism.
[unverified] Research's exact workload IAM condition strings and workload-mapping setup were not exercised. Use the shared IAM reference and current policy documentation before presenting a policy; do not copy manage-all-resources grants.
For OCIR pulls, verify registry namespace, identity-domain username, image digest, namespace-local pull secret and node egress. An OCI auth token is different from an API signing key or Console password. Do not print either.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| `error: You must be logged in to the server \(Unauthorized\)` | kubeconfig exec plugin produced no valid token: wrong CLI profile, expired session, or missing policy | id 82 [unverified] |
| `Unable to connect to the server: dial tcp .*: i/o timeout` | kubeconfig targets `PRIVATE_ENDPOINT` from outside the VCN, or Cloud Shell is in a different region | id 86 [unverified] |
