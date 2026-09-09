# Database product noun sets

Choose the product before querying. Base DB: db system → db-home → database → pluggable-database. ExaCS: db cloud-exa-infra plus cloud-vm-cluster (not cloud-exadata-infrastructure). Exascale: exascale-db-storage-vault plus exadb-vm-cluster. Cloud@Customer: exadata-infrastructure plus vm-cluster/vm-cluster-network; basecc-vm-cluster is a separate Base C@C noun.

MySQL HeatWave uses mysql db-system; the accelerator is nested at db-system heatwave-cluster. SQL uses mysql/mysqlsh, not the OCI control plane. PostgreSQL uses psql db-system; credentials, backups and engine compatibility differ from Oracle DB.

Globally Distributed Database uses distributed-database and distributed-database-v26, each with distinct distributed-db-service and distributed-autonomous-db-service trees. Choose from the deployed shard backing and documented API version. The research's interpretation of -v26 as a newer API is [unverified]; do not migrate trees based on its name. Stop/rotation affects all shards.

All resource families are regional. Discovery lists are samples; an empty enrolled fleet does not mean no databases. These mappings are CLI-help checked; no managed database was exercised.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| ExternalServerIncorrectState | A customer-owned server (DB agent, on-prem host, Exadata) is unreachable/misbehaving | id 19 [unverified] |
| `ORA-12541: TNS:no listener` | Wrong host/port, or the ADB is **STOPPED** | id 101 [unverified] |
