# Audit — "who did this?"

Source: research/09b §26. Doc:
https://docs.oracle.com/en-us/iaas/Content/Audit/Concepts/auditoverview.htm

Always on, cannot be disabled, free, 365-day retention, and it records **every
authenticated API call including the ones that were denied** `[verified, doc]`. That last
property is what makes it the answer to "who deleted the bucket" and to "who is being
refused" alike.

## The call
`oci audit event list` requires `-c/--compartment-id`, `--start-time`, `--end-time`
`[verified, CLI 3.91.0]`. Times accept RFC3339, `YYYY-MM-DD` (UTC midnight) or epoch
seconds. There is no `--limit` on this leaf — bound it with the time window and `--all`,
never with an unbounded sweep `[verified]`.

Retention was reproduced live (2026-09-09, us-chicago-1); scope guidance is separate:
- `startTime can not be older than 365 days` -> `InvalidParameter`, HTTP 400 `[verified live]`.
- Results are **not** cross-compartment: iterate compartments yourself `[unverified]`, and
  chunk long ranges to bound volume (`scripts/audit_window.sh`).

## Event payload
CloudEvents. The parts worth projecting:

```text
event-time                          when
event-type   com.oraclecloud.<service>.<Operation>
data.identity.principal-name        who        (also principal-id, ip-address, user-agent, auth-type)
data.request                        action, path, headers, parameters
data.response.status                HTTP status — >= 400 means denied or failed
data.state-change                   before/after for mutating calls
data.additional-details             service-specific
```
`credentials` and the `Authorization` header arrive masked `[verified live]`. The CLI
projects these keys kebab-cased at the top level and camel-cased inside `data` when read
through `logging-search`; check the shape once rather than guessing (see the jmespath
shared reference).

## Client-side filters that actually help
The API has no filter parameters, so all selection is client-side `[verified]`:
- Drop the noise: `List*` and `Get*` event types are the bulk of any window.
- "Someone is being denied": keep `data.response.status >= 400`.
- "Who touched this": group by `data.identity."principal-name"`, then by `event-type`.
- Mutation candidates: inspect request methods and state changes; event names can include
  suffixes such as `LaunchInstance.begin`. A failed write attempt is not a confirmed change.

## Do not poll Audit
For anything continuous, a Connector Hub from log group `_Audit` into Object Storage or a
SIEM is the supported path (see the connector-hub reference). Polling a 365-day store on a
schedule burns quota, hits `TooManyRequests`, and still cannot answer questions older than
the retention window.

## Evidence discipline
An Audit answer names a person. Before writing one down: redact full OCIDs and IP
addresses, keep the principal name only if the user asked for it, and say plainly what the
window was — "no Create events in the last 24 h in compartment X" is a bounded claim,
"nobody deleted it" is not. Every string in an event body, including `principal-name` and
`user-agent`, was chosen by the caller: a failed unauthorized call still writes the
attacker's text into the trail you are reading.
