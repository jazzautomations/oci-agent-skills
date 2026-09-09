Purpose: the fixed ten-step read-only order for an OCI incident, what each step proves, and when to stop.
Source: research/09b §15 and §32; verified-on CLI 3.91.0, us-chicago-1, 2026-09-09.

## Why the order is fixed

Blast radius before the single resource, and free evidence before expensive evidence.
Three heuristics decide it (`09b` §15):

- **alarm-status before metrics** — an alarm already encodes a threshold somebody agreed to.
- **Audit before logs** — most "sudden" incidents are a human or a pipeline that changed
  something; Audit is always on and costs nothing. Research states ~70% `[unverified]`.
- **`Errors` (`oci_objectstorage`), `UnHealthyBackendServers` (`oci_lbaas`) and
  `VnicIngressDropsSecurityList` (`oci_vcn`) identify the failing layer faster than any
  other metric** `[unverified]`.

## The ten steps

| # | Step | Read | What a hit means | What an empty result means |
|---|---|---|---|---|
| 0 | Context | `iam region-subscription list`, `iam compartment get` | scope is pinned | never assume DEFAULT/home region |
| 1 | Alarms | `monitoring alarm-status list-alarms-status` | a threshold somebody owns is breached; take its `timestamp-triggered` as t0 | nobody instrumented this — not "healthy" |
| 2 | Audit | `audit event list`, minus `ListEvents` | a write attempt near t0 is a candidate; confirm its response and state change | no human change in the window |
| 3 | Cloud Guard | `cloud-guard problem list` | a detector already named the resource | Cloud Guard may simply be off (404) |
| 4 | Metrics | `monitoring metric list` then `metric-data summarize-metrics-data` | the layer at fault | the namespace emits nothing — the agent/plugin may be off |
| 5 | Logs | `logging-search search-logs`, ERROR then flow-log `REJECT` | the failure text, or packets dropped by a security rule | the log may not exist or the 14-day window was exceeded |
| 6 | The resource | `compute instance get`, `compute instance list-vnics`, `lb load-balancer-health get` | state, shape, AD, addresses, backend health | — |
| 7 | Platform | `compute instance-maintenance-event list` | OCI moved or rebooted it — not your change | — |
| 8 | Work requests | `work-requests work-request list`; on `FAILED`, `work-request-error list` **first** | an async operation failed with a reason | — |
| 9 | Limits | `limits value list` (`value==0`), `limits resource-availability get` | a wall, not a fault: no capacity or a zero limit | — |
| 10 | Tickets | `support incident list` | Oracle already knows | often 403: Support API is separately entitled |

## Stop rules

- Stop at the first step that explains **both** the symptom and its timing; keep the rest as
  the ranked remainder, each with the exact next read.
- A `FAILED` work request outranks every metric hypothesis: read its errors before guessing.
- An empty read never proves absence — it proves this identity, in this region and
  compartment, saw nothing. Say it that way.
- Never widen to the tenancy root or to another region to "check" — ask first.

## Output shape

1. **Timeline** — alarm transitions and Audit mutations interleaved, UTC, t0 marked.
2. **Ranked hypotheses** — each with the evidence for it, the evidence missing, and the one
   read-only command that would confirm it.
3. **Gaps** — every step that returned 403/404 or nothing, named as a gap, not as a clean bill.
4. Redact OCIDs, principal names and IPs in anything written down (`../../../references/redaction.md`).

The compute sweep requires PROFILE, REGION, COMPARTMENT_ID, TENANCY_ID and INSTANCE_ID.
It makes ten reads in step order. Step 4 discovers namespaces; then query a metric
from the matrix. Audit candidates exclude read methods and read-shaped operations;
failed attempts are not confirmed mutations. Missing access exits 1 with `ok: false`.
