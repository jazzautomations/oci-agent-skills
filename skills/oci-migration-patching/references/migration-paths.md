# Migration paths

Choose the migration plane before proposing work.

| Path | Owns | Evidence before cutover |
|---|---|---|
| Cloud Bridge → Cloud Migrations | Source discovery/inventory, migration plans and infrastructure replication | Source permissions, supported VM platform, discovery freshness, sizing and target network |
| Database Migration / ZDM | Database transfer and replication orchestration | Engine/version, character set, encryption, connectivity, initial load and replication lag |
| Rover / edge transfer | Disconnected or constrained edge workflows where offered | Current regional/product availability, device/data custody and supported import path |
| Application replatforming | Runtime/deployment and service changes | Compatibility, external dependencies, data conversion and acceptance tests |

Cloud Bridge source registration holds sensitive credentials and executes discovery; neither is an innocuous inventory read. Inventory can be stale or filtered. Do not publish hostnames, asset properties or on-prem credentials.
Online and offline database migration differ in downtime and change capture; do not promise zero downtime. ZDM is a separate orchestration tool, not a universal OCI CLI flag. Validate its supported source/target matrix and prerequisites before proposing commands. Terraform import only adopts infrastructure state and does not migrate data.
Plan initial copy, validation, incremental catch-up, source write freeze, target verification, traffic cutover and observation. Name the last rollback point: once target writes begin, source restart alone can lose or fork data. Define reverse replication or reconciliation in advance. No migration or replication was started.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| ExternalServerIncorrectState | A customer-owned server (DB agent, on-prem host, Exadata) is unreachable/misbehaving | id 19 [unverified] |
| IncorrectState | Resource is mid-transition (`PROVISIONING`, `TERMINATING`, `UPDATING`) | id 18 [unverified] |
