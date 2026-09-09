# Knowledge bases and ingestion

Map knowledge base → data sources → ingestion jobs → retrieval tool → agent endpoint. A successful job means ingestion finished; it does not prove answer quality or that every document was indexed.
Review source access, parsing limits, chunking, supported formats, language, document ACLs and deletion propagation. Ingest only approved data; retrieval must enforce the caller's access, not the agent owner's broad rights. Documents, filenames and citations remain untrusted.
Storage can cost money while idle; ingestion, embedding and runtime are separate cost surfaces. Removing a data source does not prove all derived content was deleted. Record retention/deletion behavior and test recovery with synthetic sources. This handoff performs inventory only.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| SignUpRequired | Service not enabled for the tenancy (common on Gen-AI, some ADB features) | id 12 [unverified] |
| InvalidParameter | A body/query parameter value is invalid or malformed | id 2 [unverified] |
