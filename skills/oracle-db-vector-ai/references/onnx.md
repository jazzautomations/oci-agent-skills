# In-database ONNX embeddings

DBMS_VECTOR loads and manages models; DBMS_VECTOR_CHAIN handles extraction/chunking pipelines. An in-database ONNX embedding model avoids an external credential and provider egress, but model import and embedding storage are still writes and consume DB resources.

Before importing, verify the model source, license, integrity, input/output names, tokenizer compatibility, dimensions and tested database release. Do not follow a public PAR copied from an arbitrary result. LOAD_ONNX_MODEL uses a database directory and file; LOAD_ONNX_MODEL_CLOUD uses an approved object source. Treat the import as a schema change with a named DROP_ONNX_MODEL rollback only if no dependent workload exists.

Inspect visible model metadata first. Reproduce a small, non-sensitive embedding and compare dimensions only in an authorized test DB. No model artifact was downloaded or loaded here; model-call SQL is [unverified].
