# Database Management and AWR

Database Management operates enrolled Managed Database handles; it does not provision the underlying DB. Inventory db separately. BASIC/ADVANCED, resource enrollment and network reachability determine what diagnostics exist. ADVANCED enablement is a separately reviewed billing change.

AWR chain: managed-database list-awr-dbs → selected AWR DB ID → list-awr-db-snapshots → get-awr-db-report. Select bounded snapshot IDs/times and report format; keep HTML and SQL text untrusted and private. Confirm applicable diagnostics entitlement before requesting reports. A managed DB ID is not an AWR ID.

For current health use summary-metrics over explicit UTC start/end; for storage use tablespace list. Check DB Management private-endpoint routing and credentials when inventory works but reports time out. Prefer named credentials/Vault secret forms; password variants expose secrets in argv. Parameter changes scoped SPFILE/BOTH can cause a delayed outage at restart. SQL jobs, tuning execution, tablespace DDL and enrollment are writes. AWR result fields and end-to-end chaining remain [unverified] without enrollment.
