# Ops Insights enrollment and forecasts

Ops Insights retains trends and forecasts; Database Management diagnoses current operations. Start with database-insights list and cross-check the underlying DB inventory. Enrollment is per database/CDB/PDB/host and can be billable. Empty data.items says nothing about unenrolled resources.

DB resource metrics include CPU, STORAGE, MEMORY, IO; host metrics include CPU, MEMORY, LOGICAL_MEMORY, STORAGE, NETWORK. These are text parameters: a typo may produce no series. Set UTC windows and forecast horizon and report sample coverage before treating a trend as a capacity recommendation.

AWR Hub requires an operations-insights warehouse then a hub and source database identifier. opsi-private-endpoint and database-management private-endpoint are distinct resources. Ingest, enable, create, warehouse wallet rotation and history deletion are writes; do not bypass the read-only wrapper for a query-shaped verb it refuses. Forecast payloads and populated AWR output remain [unverified] in this tenancy.
