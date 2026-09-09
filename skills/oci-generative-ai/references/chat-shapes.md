# Chat and embeddings

chat_min.py --api-format GENERIC produces a local chatRequest with messages containing role USER and content entries of type TEXT. COHERE uses message, not messages. The helper sends nothing and accepts no credentials. Its synthetic prompt is suitable for a later explicitly authorized smoke check.
Serving JSON is separate: ON_DEMAND uses servingType and modelId; DEDICATED uses servingType and endpointId. Obtain IDs from discovery; use camelCase in API JSON, while CLI response projections use hyphenated keys. Supply files to the guarded chat fence only after approving region, model, data classification, max tokens and expected cost.
isStream false returns JSON; true is server-sent events and needs an SSE reader, cancellation and partial-response handling. Do not parse SSE as one JSON document. Embeddings are a separate billable inference operation with model-specific dimensions, input type and truncation behavior. Re-embed an entire index when incompatible dimensions/models change; vectors inside Oracle DB route to oracle-db-vector-ai.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| SignUpRequired | Service not enabled for the tenancy (common on Gen-AI, some ADB features) | id 12 [unverified] |
| InvalidParameter | A body/query parameter value is invalid or malformed | id 2 [unverified] |
