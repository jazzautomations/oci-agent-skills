# OKE patterns
Source: research/13 rows 20–23.
| Intent | Architecture Center book |
|---|---|
| OKE plus Autonomous DB example | cloud-native-ecommerce (MuShop), created 2025-04-28 |
| Minimal microservice cluster | deploy-microservices, created 2023-11-29 |
| Mesh/mTLS design | oci-service-mesh-oke, created 2024-11-05 |
| Trace service latency | oci-apm-for-microservices, created 2025-03-10 |
Use the shared Architecture Center reference for checked URLs. Old terraform-oci-arch stacks are illustrative and need provider/release review. [unverified] The mesh page-to-repository association was inferred in research; recheck service availability and the code link before recommending deployment. Creation dates do not prove freshness.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| `error: You must be logged in to the server \(Unauthorized\)` | kubeconfig exec plugin produced no valid token: wrong CLI profile, expired session, or missing policy | id 82 [unverified] |
| `Unable to connect to the server: dial tcp .*: i/o timeout` | kubeconfig targets `PRIVATE_ENDPOINT` from outside the VCN, or Cloud Shell is in a different region | id 86 [unverified] |
