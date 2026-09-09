# DR topology and proof

Choose backup/restore, pilot light, warm standby or active/active from the workload's allowed downtime, loss tolerance, consistency model and operating cost. Architecture Center diagrams provide starting assumptions; verify each supported service combination in the actual regions and realm.
Build a dependency order: identity/secrets/keys and networking → replicated storage/database → middleware/application → DNS/traffic → downstream integrations. Include on-prem connectivity, certificates, licenses, DNS TTL/cache behavior and third-party allowlists.
Define RPO as the acceptable lost committed work at recovery, and RTO as elapsed time from the agreed incident start to accepted service restoration. Measure actual recovered transaction positions and application acceptance timestamps. Replication lag is one input, not the whole achieved RPO; a completed infrastructure plan is not accepted service restoration.
Before a drill, agree on synthetic transactions, isolated targets, no outbound business side effects, observers and abort thresholds. Afterward record planned versus achieved RPO/RTO, missing dependencies, recovery cost and failback prerequisites. This skill prepares and inspects that evidence; no drill was run in this handoff.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| ExternalServerIncorrectState | A customer-owned server (DB agent, on-prem host, Exadata) is unreachable/misbehaving | id 19 [unverified] |
| IncorrectState | Resource is mid-transition (`PROVISIONING`, `TERMINATING`, `UPDATING`) | id 18 [unverified] |
