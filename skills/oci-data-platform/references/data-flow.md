# Spark and Batch

Data Flow application configuration is instantiated as a run; pools retain capacity, private endpoints provide network paths, and SQL endpoints/statements are another execution surface. Inspect application/run state, Spark version, shape, arguments and run-log metadata with sensitive values omitted. Logs can contain source data or credentials.
Before a run proposal, verify driver/executor runtime compatibility, Object Storage artifact and log access under the run identity, DNS/VCN reachability and regional shape availability. Budget retries, executor scaling and pool idle capacity. Running a SQL SELECT can still launch billable compute; metadata-only inspection does not do so.
OCI Batch separates context, job pool, job, task, task profile and task environment. A job owns tasks; inspect per-task failures and exit codes rather than treating job submission as completion. Container pulls, task commands and resource allocations are execution, and must be reviewed before submission.
Stopping a run can leave partial output. A rollback plan uses immutable input versions, staging output prefixes and an explicit publish step; deletion of a failed run is not data rollback.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| IncorrectState | Resource is mid-transition (`PROVISIONING`, `TERMINATING`, `UPDATING`) | id 18 [unverified] |
| ExternalServerIncorrectState | A customer-owned server (DB agent, on-prem host, Exadata) is unreachable/misbehaving | id 19 [unverified] |
