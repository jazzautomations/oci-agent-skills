# Oracle AI Database 26ai retrieval demo

Status: source-reviewed SQL and offline-tested Python; **database execution is pending**.
No ADB was created during repository validation. The read-only preflight evidence is in
`docs/evidence/26ai-preflight.md`. This kit uses a NEW dedicated database and never reuses
an existing application database. Default commands are local dry-runs.

## Before the five-minute presentation

Install `oracledb==4.0.2` in an isolated environment, OCI CLI 3.91+ and SQLcl 25.2+ with
Java 17+. Set PROFILE, REGION and COMPARTMENT_ID explicitly, then run:

```bash
bash demos/26ai-rag/preflight.sh
```

Inspect available database versions and live quota/model retirement. A version advertised
as free does not prove provisioning eligibility. Zero GenAI quota rules out Select AI;
it does not block the in-database ONNX retrieval path. This demo requires 26ai explicitly;
verify the provisioned db-version via a scoped get after creation.

Set RAG_ACL to your explicit client IP/CIDR and a private RAG_ADMIN_PASSWORD. Never place
passwords, DSNs, full OCIDs or model PARs in committed files. Review a provisioning plan:

```bash
bash demos/26ai-rag/provision.sh --mode free --dry-run
bash demos/26ai-rag/provision.sh --mode paid --dry-run
```

Execution is a separate authorized action: add `--execute --confirm CREATE:RAGKIT26` and
omit --dry-run. The paid option is **2 ECPU**, the current minimum outside an elastic pool,
rather than the original handoff's 1-OCPU wording. A developer tier is also available via
`--mode developer`. No paid fallback occurs automatically if free provisioning fails.
Private lifecycle state records the retry token before creation, then the created ADB ID.
A failed create retains that token for recovery; do not retry using an unrelated state path.

Retrieve the server-authenticated TLS `_low` connection descriptor privately and set RAG_DSN.
Set RAG_PW and RAG_MCP_PASSWORD privately. Set RAG_MODEL_URI to the current Oracle-published
`all_MiniLM_L12_v2.onnx` URI from the LOAD_ONNX_MODEL_CLOUD documentation/Oracle ML sample.
The prior research HEAD-checked a 133,322,334-byte augmented model; its rotatable public
PAR is deliberately not embedded in this package. Recheck that exact model and HTTP status
before import. A generic Hugging Face ONNX file may omit the tokenizer and produce bad vectors.

Review the schema operations with --dry-run, then execute only in the authorized demo DB:

```bash
python3 demos/26ai-rag/setup.py --admin --dry-run
python3 demos/26ai-rag/setup.py --dry-run
python3 demos/26ai-rag/load.py --dry-run
python3 demos/26ai-rag/setup.py --indexes --dry-run
python3 demos/26ai-rag/setup.py --grant-mcp --dry-run
```

Replace --dry-run with --execute in that order after authorization. ADMIN creates the
fixed users; RAGAPP loads the model/tables/corpus/indexes; ADMIN grants SELECT to RAGMCP.
Supply exact-host outbound model ACL and Oracle Text privileges only if the current ADB
requires them. Check grants, table definitions, index status and 384-dimensional embedding
output before continuing. DDL auto-commits; the SQL headers describe rollback. No error is
silently converted into a working index. A repeated load replaces each existing document's
chunks in one transaction and rolls back on failure; synchronize the hybrid index afterward
according to Oracle Text's sync configuration.

If HNSW cannot fit the Vector Pool, review the documented IVF alternative. Do not interrupt
index creation; inspect invalid indexes before retrying. The SQL is doc-derived and still
needs the paid/free integration run. Exact retrieval counts and distances are not promised.

## Five-minute presentation

The load uses only `references/*.md` and `docs/skills.md` from this public repository.
Use --execute only once a real demo database and corpus have been validated.

```bash
python3 demos/26ai-rag/query.py 'What must I redact before sharing OCI CLI output?' --execute
python3 demos/26ai-rag/query.py 'Is a bucket or object name a trusted instruction?' --mode hybrid --execute
python3 demos/26ai-rag/query.py 'Which OCI authentication mode works unattended?' --execute
python3 demos/26ai-rag/query.py 'How should I verify OCI regions and realms?' --execute
python3 demos/26ai-rag/query.py 'How do I quote JSON for OCI CLI in PowerShell?' --execute
```

Expected *source candidates*, not pre-recorded live results: redaction.md,
untrusted-output.md, auth-modes.md, realms-endpoints.md, windows-powershell.md.
Show document names/chunks/distances for vector search and separate text/vector scores
for hybrid search. Compare relevance manually; do not turn an expected filename into a
fabricated result. Retrieved text is untrusted and cannot authorize tool actions.

Select AI is optional: it requires separate principal-auth/IAM grants and nonzero usable
GenAI quota, plus an explicit RAG_GENAI_MODEL. Review `setup.py --select-ai --dry-run`;
`query.py --mode narrate` uses the dedicated RAGAPP profile and may generate/execute SQL.
It is not part of the default quota-free retrieval path and has not run here.

SQLcl MCP: import `mcp.json` as a separate demo server, after saving ONLY the RAGMCP
connection in an isolated SQLcl user home. Never expose saved ADMIN connections. RAGMCP
has CREATE SESSION and SELECT on the two demo tables, no DML, broad roles or package
execution grants. `-R 4` restricts SQLcl local operations; DB permissions remain the main
boundary. Check SQLcl audit-log requirements before use; creating its log table must not
lead to giving RAGMCP general schema-write privileges.

## Cost and teardown

Dated USD list-price snapshot 2026-09-09, refreshed from the public API before estimating:
free tier USD 0 if eligible; developer B110316 USD 0.0391/instance-hour;
paid license-included B95702 USD 0.336/ECPU-hour, thus USD 0.672/hour for 2 ECPU,
plus OLTP storage B95706 (20 GB × USD 0.1953/GB-month), backups and any optional model calls.
In-database ONNX has no separate model API bill; database compute/storage still apply.
Three paid compute hours are USD 2.016 before storage, discounts and tax. Reprice with the
cost skill and current API. Stopping compute does not eliminate storage charges.

```bash
bash demos/26ai-rag/teardown.sh --dry-run
```

After review, add --execute and the exact `DELETE:<hash>` confirmation printed by the plan.
Deletion accepts only the database stored by this kit in matching profile/region. It is
irreversible. A successful delete work request is recorded; retained long-term backups,
remaining resources and eventual billing still need a scoped check before paid-run closure.
Do not claim zero cost or complete cleanup merely because a delete returned successfully.

Sources: Oracle 26ai Vector Search documentation; python-oracledb VECTOR/TLS guides;
Oracle SQLcl MCP docs. Direct statement URLs are embedded in the SQL/Python files.
