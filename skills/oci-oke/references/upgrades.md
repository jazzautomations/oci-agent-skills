# Upgrades
Source: research/09a §19.
Inventory control-plane version, node pool versions/images, add-ons, workloads and PodDisruptionBudgets before choosing the next supported version. Upgrade the control plane before workers, respecting supported minor-version steps and skew.
Plan surge capacity, drain grace and rollback limits. Enhanced node cycling and a replacement pool have different recovery behavior; check cluster type first. Preserve the old pool until workloads and storage are healthy.
Control-plane upgrade has no general downgrade rollback. Treat it as an irreversible proposal with a recovery/migration plan. Credential rotation and public-endpoint decommission have separate deadlines and recovery procedures.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| `error: You must be logged in to the server \(Unauthorized\)` | kubeconfig exec plugin produced no valid token: wrong CLI profile, expired session, or missing policy | id 82 [unverified] |
| `Unable to connect to the server: dial tcp .*: i/o timeout` | kubeconfig targets `PRIVATE_ENDPOINT` from outside the VCN, or Cloud Shell is in a different region | id 86 [unverified] |
