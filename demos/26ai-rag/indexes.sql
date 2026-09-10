-- MUTATING — not run in this repo. Run AFTER ingest; no invalid-index errors are suppressed.
-- https://docs.oracle.com/en/database/oracle/oracle-database/26/vecse/hierarchical-navigable-small-world-index-syntax-and-parameters.html
DECLARE n NUMBER;
BEGIN
  SELECT COUNT(*) INTO n FROM user_indexes WHERE index_name='DOC_CHUNKS_HNSW';
  IF n=0 THEN
    EXECUTE IMMEDIATE 'CREATE VECTOR INDEX doc_chunks_hnsw ON doc_chunks(embedding) ORGANIZATION INMEMORY NEIGHBOR GRAPH DISTANCE COSINE WITH TARGET ACCURACY 95 PARAMETERS (TYPE HNSW, NEIGHBORS 32, EFCONSTRUCTION 300)';
  END IF;
END;
/
-- https://docs.oracle.com/en/database/oracle/oracle-database/26/vecse/query-hybrid-vector-indexes-end-end-example.html
DECLARE n NUMBER;
BEGIN
  SELECT COUNT(*) INTO n FROM user_indexes WHERE index_name='REFS_HYBRID_IDX';
  IF n=0 THEN
    EXECUTE IMMEDIATE 'CREATE HYBRID VECTOR INDEX refs_hybrid_idx ON doc_tab(text) PARAMETERS(''model ALL_MINILM_L12_V2'')';
  END IF;
END;
/
