# HNSW, IVF and query plans

Match the index and VECTOR_DISTANCE metric exactly; otherwise Oracle may run an exact scan. Do not wrap VECTOR_DISTANCE in another function. DOT is negative dot product; INNER_PRODUCT has the opposite sign. Record exact-search recall and latency before choosing approximate accuracy.

HNSW needs a vector memory pool; IVF uses centroid partitions and substantial temporary space. IVF cannot index sparse vectors, becomes UNUSABLE after TRUNCATE and may lose recall after DML. Inspect USER_INDEXES index type/subtype/state. On ADB use V$VECTOR_INDEX when granted, not inaccessible VECSYS.VECTOR$INDEX. Rebuilds and memory changes are separate reviewed writes.

[unverified SQL; existing doc_chunks and a correctly typed :qvec bind required]
```sql
SELECT id
FROM doc_chunks
ORDER BY VECTOR_DISTANCE(embedding, :qvec, COSINE)
FETCH APPROX FIRST 5 ROWS ONLY;
```
Only one vector index type can serve a vector column. Verify the execution plan through an authorized diagnostics session; EXPLAIN PLAN can write PLAN_TABLE and is not in the read-only script.

## Diagnostic signals

| Error string | Distinguish | Source |
|---|---|---|
| ORA-01031 / ORA-00942 | Missing privileges or inaccessible objects can prevent a feature probe; do not infer feature absence from that result. | research/08a read-only identity checks [unverified] |
