# Exadata Fleet Update

The CLI group is fleet-software-update. Collections select compatible targets; cycles coordinate maintenance; actions execute stages; jobs and outputs report per-target work. List forms use fsu-collection-summary, fsu-cycle-summary, fsu-action-summary and fsu-job-summary.
Check target membership and type, current/target versions, supported update strategy, maintenance window and existing cycle state. Discovery and readiness checks can launch work and write results; the word check does not establish read-only behavior.
Separate Grid Infrastructure, database home/software and guest OS responsibilities. Database services, standby configuration and application dependencies affect whether a rolling strategy preserves availability.
Stage and canary before broad execution, record per-target state and work-request IDs, and validate application connectivity/performance afterward. A failed action may have succeeded on some targets. Rollback eligibility depends on patch type and stage; obtain the supported procedure and backups rather than inventing a universal undo. No action or readiness job was run.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| ExternalServerIncorrectState | A customer-owned server (DB agent, on-prem host, Exadata) is unreachable/misbehaving | id 19 [unverified] |
| IncorrectState | Resource is mid-transition (`PROVISIONING`, `TERMINATING`, `UPDATING`) | id 18 [unverified] |
