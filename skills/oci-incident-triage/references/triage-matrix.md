Purpose: symptom -> metric namespace -> metric -> log query, so step 4 and step 5 never guess.
Source: research/09b §1, §5, §7, §15; verified-on CLI 3.91.0, us-chicago-1, 2026-09-09.

## Rule zero

**Never guess a namespace.** Ask the tenancy what it actually emits, then query:

```bash
oci monitoring metric list --compartment-id "$COMPARTMENT_ID" --compartment-id-in-subtree true --limit 200 --query 'data[].namespace' --raw-output
```

On 2026-09-09 this tenancy returned seven: `oci_autonomous_database`, `oci_blockstore`,
`oci_compute_infrastructure_health`, `oci_generativeai`, `oci_logging`, `oci_objectstorage`,
`oci_vcnip` `[verified]`. A namespace absent here emits nothing today — that is a gap in the
evidence, not a healthy resource. Every row below that this tenancy does not emit is
`[unverified]`: namespace names come from the per-service docs, not from a live read.

## Symptom -> where to look

| Symptom | Namespace | Metric | Log / next read |
|---|---|---|---|
| VM slow, high load | `oci_computeagent` | `CpuUtilization`, `MemoryUtilization`, `LoadAverage` | needs the Compute plugin; if silent use `oci_compute` |
| VM unreachable, "worked yesterday" | `oci_compute_infrastructure_health` | `InstanceAccessibilityStatus`, `MaintenanceStatus` | `compute instance-maintenance-event list` |
| Disk latency, I/O stalls | `oci_blockstore` | `VolumeThrottledIOs`, `VolumeReadThroughput` | VPU setting, not a fault |
| Connections time out, packets vanish | `oci_vcn` | `VnicIngressDropsSecurityList`, `VnicConntrackFullDropPackets` | flow-log `REJECT` query below |
| No public IPs left | `oci_vcnip` | `IpAvailable`, `IpUsed` | `limits value list --service-name vcn` |
| 5xx behind a load balancer | `oci_lbaas` | `UnHealthyBackendServers`, `HttpResponses5xx` | `lb load-balancer-health get` |
| 5xx behind an NLB | `oci_nlb` | `HealthyBackendCount` | `nlb network-load-balancer-health get` |
| Bucket errors, slow objects | `oci_objectstorage` | `Errors`, `TotalRequestLatency` | Audit `event-type` on the bucket |
| Database sessions piling up | `oci_autonomous_database` | `CpuUtilization`, `Sessions`, `ApplyLag` | ADB lifecycle state first |
| Functions failing | `oci_faas` | `FunctionResponseCount`, `FunctionExecutionDuration` | function log in Logging |
| Cluster pods pending | `oci_oke` | `UnschedulablePods`, `NodeCondition` | node pool + limits |
| Logs stopped arriving | `oci_logging` | `IncomingLogEvents`, `DroppedLogEvents` | agent config, not the app |

## The two log queries that matter in triage

Errors in the window, newest first:

```bash
oci logging-search search-logs --search-query "search \"$COMPARTMENT_ID\" | where \"data.level\" = 'ERROR' | sort by datetime desc" --time-start "$START_TIME" --time-end "$END_TIME" --limit 100 --query 'data.results[].data.datetime'
```

Packets dropped by a security rule, grouped by destination:

```bash
oci logging-search search-logs --search-query "search \"$COMPARTMENT_ID\" | where \"data.action\" = 'REJECT' | summarize count() by \"data.destinationAddress\"" --time-start "$START_TIME" --time-end "$END_TIME" --limit 100 --query 'data.results[].data'
```

Both need the log to exist: `oci logging log-group list` and `oci logging log list` first
(that is `oci-logging-audit`'s ground, and the search window is 14 days).

## Resolution and retention

Query resolution caps the range: `1m` -> 7 days, `5m` -> 30 days, `1h`/`1d` -> 90 days.
A 3-hour incident window wants `[1m]` or `[5m]`; `[1m]` on an hourly metric returns nothing
and looks like an outage.
