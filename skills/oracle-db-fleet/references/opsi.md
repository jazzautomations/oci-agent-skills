# Ops Insights enrollment and forecasts

Ops Insights retains trends and forecasts; Database Management diagnoses current operations. Start with database-insights list and cross-check the underlying DB inventory. Enrollment is per database/CDB/PDB/host and can be billable. Empty data.items says nothing about unenrolled resources.

DB resource metrics include CPU, STORAGE, MEMORY, IO; host metrics include CPU, MEMORY, LOGICAL_MEMORY, STORAGE, NETWORK. These are text parameters: a typo may produce no series. Set UTC windows and forecast horizon and report sample coverage before treating a trend as a capacity recommendation.

AWR Hub requires an operations-insights warehouse then a hub and source database identifier. opsi-private-endpoint and database-management private-endpoint are distinct resources. Ingest, enable, create, warehouse wallet rotation and history deletion are writes; do not bypass the read-only wrapper for a query-shaped verb it refuses. Forecast payloads and populated AWR output remain [unverified] in this tenancy.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| ExternalServerIncorrectState | A customer-owned server (DB agent, on-prem host, Exadata) is unreachable/misbehaving | id 19 [unverified] |
| `ORA-12541: TNS:no listener` | Wrong host/port, or the ADB is **STOPPED** | id 101 [unverified] |
