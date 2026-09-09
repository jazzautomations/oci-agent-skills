# Logging Analytics (LQL) — the other query language

Source: research/09b §8. Doc: https://docs.oracle.com/en-us/iaas/logging-analytics/home.htm

Logging Analytics is a **different service** from Logging, with a different query language
(**LQL**, not the `logging-search` grammar), a separate per-tenancy namespace, and a price:
per-GB ingest plus active storage, where plain Logging search is free `[unverified]`. Reach
for it only when the user needs parsing, entity correlation, ML anomaly detection,
dashboards, or retention past the 14-day search window.

## Is it even on?
```text
oci log-analytics namespace list --compartment-id <tenancy> --all
  -> data.items[].{ns:"namespace-name", on:"is-onboarded"}
```
`[verified live 2026-09-09, us-chicago-1]`: one namespace row, `is-onboarded: false`. A
namespace existing does **not** mean the tenancy is onboarded — check the flag before
proposing any LA work, or every later call fails for a reason that looks like a permission
problem.

## The commands that matter `[verified: group shape, CLI 3.91.0]`
The `log-analytics` group exposes `namespace`, `query`, `source`, `parser`, `entity`,
`storage`, `scheduled-task`, `object-collection-rule`, `ingest-time-rule`, `upload`,
`lookup`.

```text
log-analytics query query --namespace-name <ns> --compartment-id <c>
  --query-string "'Log Source' = 'Linux Syslog Logs' | stats count by 'Host Name'"
  --sub-system LOG --time-start <rfc3339> --time-end <rfc3339>
log-analytics source list-sources --namespace-name <ns> --compartment-id <c> --all
log-analytics entity list-log-analytics-entities --namespace-name <ns> --compartment-id <c>
log-analytics object-collection-rule list --namespace-name <ns> --compartment-id <c>
```
All four are `[unverified]` against a live namespace here — the reference tenancy is not
onboarded, so only their `--help` shape was checked.

## LQL is not the search grammar
LQL names fields in single quotes (`'Log Source'`, `'Host Name'`) and pipes into `stats`,
`timestats`, `classify`, `link`. Writing a `search "<compartment>" | where …` string into
`--query-string` will fail; so will the reverse. Decide which service answers the question
*before* composing a query, and say which one you used in the answer.

## The cheap ingestion path
An **Object Collection Rule** pointed at an Object Storage bucket that a Connector Hub is
already filling needs no agent at all `[unverified]`. When a user wants "logs older than 14
days, searchable", that pairing — Connector Hub to a bucket, LA object-collection-rule over
the bucket — is the shape to propose, with the cost stated plainly.

## Cost honesty
Never propose onboarding Logging Analytics, creating an object-collection-rule, or
enabling ingest without saying that it is a paid service billed on ingest and active
storage, and that the free `logging-search` path already answers anything inside 14 days.
This skill proposes; it does not create.
