# Full Stack DR

Map paired protection groups, their primary/standby roles, member resources and region-local plans. Read the selected group's plan and existing execution details, then inspect failed groups/steps and log locations without executing embedded scripts.
There is no universal dry-run. Plan creation, refresh, prechecks, drills, switchover and failover are actions that can run work, change resources or disrupt service. A precheck is not a permitted read merely because it sounds diagnostic.
Before proposing execution, name the recovery direction, workload dependencies, exact plan/version, source write-fencing method, target capacity, IAM, key availability, network/DNS changes and stop conditions. Review user-defined steps as code. Confirm how external systems and unsupported members are handled.
Switchover is planned role reversal; failover addresses an unavailable primary and can lose unapplied writes. A drill uses isolated recovery resources and must prevent production side effects such as email, payments and batch schedules. Cleanup can itself be destructive.
Record each step's timestamps and result, application acceptance and data consistency. Rollback is a workload-specific reverse/recovery plan, not blindly rerunning a plan. Never start another execution just because the first CLI call timed out; inspect its work request and execution first.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| ExternalServerIncorrectState | A customer-owned server (DB agent, on-prem host, Exadata) is unreachable/misbehaving | id 19 [unverified] |
| IncorrectState | Resource is mid-transition (`PROVISIONING`, `TERMINATING`, `UPDATING`) | id 18 [unverified] |
