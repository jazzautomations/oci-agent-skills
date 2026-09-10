# HANDOFF 13 → Codex — 26ai RAG kit (`demos/26ai-rag/`) ready to execute on Saturday with a real ADB

Branch main. Ground rules as always. TODAY: build everything that does not need a database, verify every SQL/API statement against
the docs cited in the research, and make the run scripts idempotent with a --dry-run that prints the plan. Do NOT create an ADB
now (no credits yet). Commit per item, push, CODEX-STATUS.md.
INPUTS: research/20-26ai-rag-kit.md, research/26-26ai-real-problems.md (20 pitfalls + preflight checklist), research/27-26ai-deep-study.md
(file-by-file spec, SQL, python-oracledb, SQLcl MCP, ADB create/delete CLI, GenAI models), skills/oracle-db-vector-ai, skills/oracle-autonomous-db,
skills/oracle-db-sql-access, research/08a, 08b.
DELIVER:
1. demos/26ai-rag/README.md (the 5-minute demo script: what to type, expected output, cost per hour, teardown), preflight.sh (checks
   from 26: CLI version, region, ADB version availability via `oci db autonomous-db-version list`, GenAI models via
   `oci generative-ai model list`, SQLcl + Java present, python-oracledb version) — read-only, run it now and record output.
2. provision.sh: `oci db autonomous-database create` (free tier variant AND paid 1-OCPU variant, both with --wait-for-state) with all
   flags verified; teardown.sh (delete with confirmation); both marked MUTATING; --dry-run prints the exact command.
3. setup.sql: app user, VECTOR table, ONNX model load (DBMS_VECTOR.LOAD_ONNX_MODEL from object storage or LOAD_ONNX_MODEL_CLOUD) with
   the exact model URL from 27, chunking + embedding pipeline (DBMS_VECTOR_CHAIN), HNSW index, hybrid vector index, Select AI profile
   for OCI GenAI (attributes verified). Every statement carries a comment with its doc URL.
4. load.py / query.py (python-oracledb thin, TLS no wallet): load corpus = this repo's references/*.md + docs/skills.md; query = vector,
   hybrid, and Select AI narrate; 5 demo questions with expected retrieved chunks; unit tests with a fake connection.
5. mcp.json for SQLcl MCP (`sql -mcp`) with a read-only DB user; docs/26ai.md; README row. Update skills/oracle-db-vector-ai to route
   to the demo. All validators green; tests green.
