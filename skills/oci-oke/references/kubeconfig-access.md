# Kubeconfig access
Source: research/09a §14; research/14 §9.
The kubeconfig exec plugin needs OCI CLI, the intended profile/auth context and network access to the selected endpoint at every use. IAM authorization and Kubernetes RBAC are separate checks.
Use token-version 2.0.0; the installed CLI rejects 1.0.0. When requested, propose create-kubeconfig to a new user-selected local file, preserving the existing config. It writes local credentials and is refused by oci_ro even though it does not mutate the tenancy.
A PRIVATE_ENDPOINT requires an approved VCN path such as VPN/Bastion/private runner. Do not make the endpoint public as an authentication fix.
[unverified] Research reports noninteractive token-expiry prompts hanging kubectl; inspect a bounded CLI read and session status before retrying Kubernetes.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| `error: You must be logged in to the server \(Unauthorized\)` | kubeconfig exec plugin produced no valid token: wrong CLI profile, expired session, or missing policy | id 82 [unverified] |
| `Unable to connect to the server: dial tcp .*: i/o timeout` | kubeconfig targets `PRIVATE_ENDPOINT` from outside the VCN, or Cloud Shell is in a different region | id 86 [unverified] |
