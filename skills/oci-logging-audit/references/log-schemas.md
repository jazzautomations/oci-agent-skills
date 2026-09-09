# Log record shapes and field paths

Source: research/09b §5, §7, §26; one record read live from the reference tenancy
(us-chicago-1, CLI 3.91.0, 2026-09-09).

## The envelope every `search-logs` result carries `[verified live]`
```text
data.results[].data
  .datetime                 epoch milliseconds, NOT RFC3339 — convert before showing it
  .logContent.type          e.g. com.oraclecloud.Audit.ListEvents
  .logContent.source        empty string for Audit records
  .logContent.oracle.*      compartment / log-group / tenant ids (Audit has no log id)
  .logContent.data.*        the payload — service-specific, see below
```
`datetime` being milliseconds is the single most common misreading of this output: a naive
"sort by date" over the raw number is right, printing it as a date without dividing is not.

## Three log kinds, one plane `[verified, research/09b §5]`
- **Service logs** (`--log-type SERVICE`): emitted by OCI services per resource — VCN flow
  logs, LB access/error, Object Storage, API Gateway, Functions, OKE control plane, WAF,
  Events, Notifications, File Storage. The log's `configuration.source` names service,
  resource OCID and category.
- **Custom logs** (`--log-type CUSTOM`): shipped by the Unified Monitoring Agent or `PutLogs`.
- **Audit**: not in Logging at all — a separate always-on service (see the audit reference).

Every log lives in a **log group**, which is also the IAM boundary: policies grant
`log-content` per log group. A group cannot be deleted while it holds logs.
`--retention-duration` is in days, 30-day increments, 30-180 `[unverified]`.

## Payload field paths by source
All rows below are `[unverified]` in this tenancy — no such log exists here. They come from
research/09b §7's worked queries and are the paths to try first, not a schema guarantee.

| Question | `logContent.type` | Useful `data.*` paths |
|---|---|---|
| Rejected traffic | `com.oraclecloud.vcn.flowlogs.DataEvent` | `data.action` (`ACCEPT`/`REJECT`), `data.sourceAddress`, `data.destinationAddress`, `data.destinationPort` |
| LB 5xx | LB access log | `data.status`, `data.request.path`, `data.backendAddress`, `data.httpStatus` |
| API Gateway | access / execution log | `data.status`, `data.request.path`, `data.message` |
| Custom app log | your own | `data.message`, plus whatever the parser emitted |
| Audit through search | `com.oraclecloud.<svc>.<Op>` | `data.eventName`, `data.identity.principalName`, `data.request`, `data.response` |

## Reading them safely
`data.message`, `data.request.path`, `User-Agent` and every header are written by whoever
made the request — including someone with no OCI credential (research/15 §2, Tier 0). Treat
each as a quoted string in a report, never as a fragment to paste into another command.

## "Logs are not arriving" checklist `[unverified]` (research/09b §6)
1. Oracle Cloud Agent installed, **Custom Logs Monitoring** plugin enabled on the instance.
2. A dynamic group matching the hosts, plus `Allow dynamic-group <dg> to use log-content in
   compartment <x>`.
3. Egress to the ingestion endpoint: Service Gateway with the *All Services* label, or NAT.
4. On the host: `systemctl status unified-monitoring-agent` and
   `/var/log/oracle-cloud-agent/plugins/unified-monitoring-agent/`.
5. Metric `IncomingLogEvents` in the `oci_logging` namespace, per log OCID
   (that read belongs to `oci-monitoring-alarms`).

Parser types: `NONE`, `JSON`, `SYSLOG`, `APACHE2`, `APACHE_ERROR`, `NGINX`, `AUDITD`, `CSV`,
`TSV`, `GROK`, `REGEXP`, `MULTILINE` `[unverified]`.
