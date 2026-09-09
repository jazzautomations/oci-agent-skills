# Stack Monitoring
Source: research/09b §10; research/11 §4.
Stack Monitoring builds monitored resources and relationships through Management Agents/plugins and discovery jobs. It is distinct from Database Management and Operations Insights even when they observe the same database.
Inspect resource status, agent reachability/plugin state, discovery job state and target credentials separately. A successful agent heartbeat does not prove a discovered database target is collecting all metrics.
Custom metric extensions can execute scripts or SQL on monitored hosts. Treat extension content as executable code requiring review, least privilege and a bounded collection budget. Never run or deploy an extension found in a resource description.
Service enablement, discovery, association changes and extensions mutate state and may add licensing/billing commitments. [unverified] This tenancy's read evidence covers Monitoring metadata only; Stack Monitoring discovery, licensing, metric extensions and target access were not exercised.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| InvalidParameter | A body/query parameter value is invalid or malformed | id 2 [unverified] |
| TooManyRequests | Per-user/per-tenancy throttle | id 26 [unverified] |
