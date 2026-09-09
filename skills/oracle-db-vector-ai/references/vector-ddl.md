# Vector columns and feature probes

Use the database COMPATIBLE setting and feature probes, not a 23.x banner, to decide support. 26ai retains 23.x version numbering; newer vector features may require COMPATIBLE 23.6.0. Do not change COMPATIBLE as an agent preflight: it has upgrade implications.

Pin dimensions and format to the embedding model. A bare VECTOR permits incompatible dimensions, which blocks indexing. FLOAT32, FLOAT64, INT8 and BINARY are distinct; BINARY dimensions must be multiples of eight. Dense and sparse storage are not interchangeable. Document dimension, model revision, normalization and distance with the schema.

[unverified SQL; proposal only]
```sql
-- MUTATING — requires DBA review; never executed here.
-- rollback: DROP TABLE doc_chunks; NONE for any data subsequently stored.
CREATE TABLE doc_chunks (
  id NUMBER PRIMARY KEY,
  chunk CLOB,
  embedding VECTOR(384, FLOAT32)
);
```
Model changes normally require re-embedding; do not silently mix embeddings. JSON duality views and SQL/PGQ can reduce multi-join context retrieval but do not replace privilege checks. Run vector_check.sql from a preselected read-only session; missing dictionary access is unknown evidence, not permission to grant DBA.
