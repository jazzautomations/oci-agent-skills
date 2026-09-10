# Reproducible RAG demonstration

Source kit: https://github.com/jazzautomations/oci-agent-skills/tree/main/demos/26ai-rag

| Signal | Required action |
|---|---|
| GenAI quota zero | Use the in-database augmented MiniLM ONNX model |
| Advertised free 26ai version | Still check provisioning eligibility; no automatic paid fallback |
| Paid sizing | Use current ECPU minimum and price snapshot, not stale 1-OCPU wording |
| Missing model / ORA-01031 | Check the current Oracle model URI and exact grants |
| Invalid HNSW/hybrid index | Inspect status; never suppress a failed DDL as success |
| Missing live database | Mark SQL and retrieval evidence pending |

The kit creates a dedicated DB, loads only public repo documentation and offers five
retrieval questions. Credentials, TLS descriptors, OCIDs and model PARs remain local.
SQLcl uses a separate SELECT-only account with no saved ADMIN connection exposed.
The setup/teardown scripts are separate from this read-only skill runtime.
Source reviewed 2026-09-10; no database execution claimed.
