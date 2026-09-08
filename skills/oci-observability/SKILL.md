---
name: oci-observability
description: Diagnose OCI incidents using Monitoring, Logging, Audit, APM and Logging Analytics with bounded queries and evidence-based recovery.
---

Read [the operator contract](../../docs/operations.md). Establish incident time in
UTC, affected service, region, compartment and customer-visible symptom. Catalog
examples `sre-alarms` and `sre-log-groups` discover observability configuration.

```bash
oci monitoring alarm list --help
oci monitoring metric-data summarize-metrics-data --help
oci logging log-group list --help
oci logging-search search-logs --help
oci audit event list --help
```

Monitoring MQL, Logging search, Logging Analytics and Resource Search are different
query languages. Discover metric namespaces/dimensions and log schema before
composing a query. Use an explicit recent start/end; never silently default to a
fixed historical date or query every log in a tenancy.

Correlate request/work-request IDs, deployment time, resource lifecycle, metrics,
logs and application traces. Preserve exact observation timestamps. No returned
rows can mean wrong region, missing log ingestion/grant, field mismatch or delay.
Check these before declaring that no incident occurred.

Construct a causal hypothesis, a bounded read that can disprove it, and the smallest
authorized remediation. Capture before/after evidence and a rollback. Notifications,
Service Connector destinations and custom telemetry ingestion are writes that can
expose data or trigger downstream actions; do not enable them during passive triage.

Use service-level objectives and an application probe to verify recovery. A green
resource lifecycle alone is insufficient. Redact customer payloads and secrets
before attaching logs to a support case or incident document.

[Monitoring](https://docs.oracle.com/en-us/iaas/Content/Monitoring/home.htm),
[Logging](https://docs.oracle.com/en-us/iaas/Content/Logging/home.htm)
