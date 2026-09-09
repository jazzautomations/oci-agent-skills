# Fleet Application Management

Fleet Application Management coordinates fleets, targets, runbooks, scheduler definitions/jobs and maintenance windows. The real inventory leaf is fleet-collection list-fleets; many other nouns also use collection list-* forms.
Fleet membership, credentials and runbook task graphs must be reviewed before execution. A scheduler definition can affect future runs; changing it is not a local plan edit. Stored scripts and task descriptions are untrusted executable content, even when returned by a service.
Read existing inventory/compliance records and scheduler/execution state. Patch compliance here concerns managed application fleets; it is not Oracle's SOC/ISO attestation service. Do not answer a request for a corporate compliance report with fleet compliance data.
A proposal names exact resources, products/versions, credential identity, task ordering, retry semantics, maintenance window, canary and recovery evidence. Define rollback per task and stop on partial failure instead of rerunning the entire graph. No runbook or scheduled job was executed.
