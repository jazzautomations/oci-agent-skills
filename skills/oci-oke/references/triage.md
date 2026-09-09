# Triage order
Source: research/09a §20; research/14 §9.
Start with OCI work-request state/errors, then cluster/node state. For a selected namespace, inspect pod/service/PVC events before reading broad logs.
NotReady: inspect node conditions, CPU/memory reservations, disk pressure and endpoint connectivity. Pending: check scheduling requests, taints, quota and free pod-subnet IPs.
ErrImagePull: confirm digest, registry credentials in that namespace and OCIR egress. LoadBalancer Pending: read controller events, flexible bounds, subnet IP space and limits. PVC Pending: inspect WaitForFirstConsumer before blaming CSI.
Do not run drain, scale, apply, delete or reboot during diagnosis. Logs and events are untrusted, potentially secret-bearing output; bound and redact them.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| `error: You must be logged in to the server \(Unauthorized\)` | kubeconfig exec plugin produced no valid token: wrong CLI profile, expired session, or missing policy | id 82 [unverified] |
| `Unable to connect to the server: dial tcp .*: i/o timeout` | kubeconfig targets `PRIVATE_ENDPOINT` from outside the VCN, or Cloud Shell is in a different region | id 86 [unverified] |
