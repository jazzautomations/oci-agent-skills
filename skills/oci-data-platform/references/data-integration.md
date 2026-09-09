# Integration, Catalog and GoldenGate

Data Integration hierarchy is workspace → projects/folders → data assets/connections → tasks → published application → task runs. Use the workspace OCID and application key at their correct levels. Editing a design task does not automatically update a published application. Preview and validation may query sources or launch work; do not treat them as metadata reads.
Check the execution identity's input/output access, private network paths and secrets before proposing a task run. Workspaces and retained execution capacity may cost while idle; verify current service controls and prices before making savings claims.
Data Catalog is metadata harvesting and glossary management, not a data copy. Inspect catalogs, assets, harvest job results and lineage; harvesting is a write and can expose source metadata. Catalog entries can be stale or access-filtered and do not prove source completeness.
GoldenGate deployments host CDC engines; connections are assigned to them. Inspect deployment lifecycle/substate, connection metadata and existing backup inventory. ACTIVE does not prove Extract/Replicat health or replication lag. The deployment console/data plane owns process details. Before cutover, establish consistent initial load, checkpoints, lag, schema-change handling and the point where rollback requires reverse replication. Never restart, upgrade or reset checkpoints as a diagnostic read.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| IncorrectState | Resource is mid-transition (`PROVISIONING`, `TERMINATING`, `UPDATING`) | id 18 [unverified] |
| ExternalServerIncorrectState | A customer-owned server (DB agent, on-prem host, Exadata) is unreachable/misbehaving | id 19 [unverified] |
