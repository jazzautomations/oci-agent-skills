# Connector Hub — how logs leave the 14-day window

Source: research/09b §13. Doc: https://docs.oracle.com/en-us/iaas/Content/connector-hub/home.htm

One resource: **source -> optional task (a log filter, or a Function) -> target**. This is
how logs get archived, streamed to a SIEM, or turned into metrics. When a question cannot be
answered inside the 14-day search window, the honest answer is "that data was never kept —
here is the connector that would keep it from now on", not a wider search.

## Read what already exists
```text
oci sch service-connector list --compartment-id <c> --limit 20 --query 'data'
  -> data.items[].{n:"display-name", s:"lifecycle-state"}
```
`[verified live 2026-09-09, us-chicago-1]`: the call succeeds and returns an empty list in a
tenancy with no connectors. Watch for `lifecycle-state: NEEDS_ATTENTION` — see the policy
trap below.

## Source and target shapes `[unverified]` (research/09b §13)
Source, Logging kind — the literal `logGroupId` **`_Audit`** is the magic value for the
tenancy audit log, and it is the single most useful connector an SRE builds:
```json
{"kind": "logging",
 "logSources": [{"compartmentId": "<compartment>", "logGroupId": "_Audit"},
                {"compartmentId": "<compartment>", "logGroupId": "<group>", "logId": "<log>"}]}
```
Target, Object Storage:
```json
{"kind": "objectStorage", "namespace": "<ns>", "bucketName": "log-archive",
 "objectNamePrefix": "audit", "batchRolloverSizeInMBs": 100, "batchRolloverTimeInMs": 420000}
```
Other target kinds: `streaming`, `monitoring` (log to metric), `notifications`, `functions`,
`loggingAnalytics`.

## The trap that produces a dead connector
A connector needs an IAM policy allowing the Service Connector Hub **service principal** to
write to the target. The Console autogenerates that policy; **the CLI does not**
`[unverified]`. A connector created from the CLI without it sits in `NEEDS_ATTENTION` and
silently moves nothing. Monitor `ServiceConnectorHubErrors` in the
`oci_service_connector_hub` metric namespace (that read belongs to `oci-monitoring-alarms`).

## Cost model `[unverified]`
You pay the *target* — Object Storage or Streaming — plus a per-GB charge for what the
connector moves. Say both out loud when proposing one; a flow-log connector on a busy
subnet is the classic surprise bill. On the source side, enabling VCN flow logs on a subnet
is subnet-wide and very high volume: `category: reject` (drops only) is the cheap variant
`[unverified, research/09b §5]`.

## This skill does not create connectors
Creating one is a mutation, and it belongs to the user or to a guarded-write skill. What
this skill does: read the existing connectors, explain which one would have answered the
question, name the target and the policy it needs, and hand back the shape above for the
user to review. Never run `sch service-connector create` from here.
