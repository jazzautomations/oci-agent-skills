Purpose: query what the tenancy actually spent, with the parameters the service really accepts.
Source: research/09c B6, research/04b §19; verified-on CLI 3.91.0, us-chicago-1, 2026-09-09.

## 1. The one command

`oci usage-api usage-summary request-summarized-usages` backs Console Cost Analysis. Four flags
are `[required]`: `--tenant-id`, `--time-usage-started`, `--time-usage-ended`, `--granularity`.
Omit one and the CLI stops before any call with
`Error: Missing option(s) ...` [verified]. Times accept several formats including bare
`YYYY-MM-DD` (UTC midnight) and epoch seconds [verified, help].

- `--granularity` `HOURLY|DAILY|MONTHLY|TOTAL`. The help marks `TOTAL` not yet supported; the service answers
  `InvalidParameter` / `"Unknown Granularity"`, status 400 [verified, reproduced 2026-09-09].
  Sum locally instead.
- `--query-type` `USAGE|COST|CREDIT|EXPIREDCREDIT|ALLCREDIT|USAGE_ONLY`, **defaults to `COST`**
  [verified, help]. `USAGE` returns quantities, not money.
- `--group-by` is a JSON array of: `tagNamespace`, `tagKey`, `tagValue`, `service`, `skuName`,
  `skuPartNumber`, `unit`, `compartmentName`, `compartmentPath`, `compartmentId`, `platform`,
  `region`, `logicalAd`, `resourceId`, `tenantId`, `tenantName` [verified, help].
- `--group-by-tag` is separate and **"Only supports one tag in the list"**: pass
  `'[{"namespace":"Oracle-Tags","key":"CreatedBy"}]'` [verified, executed — returned per-tag
  `computed-amount` rows]. Grouping by a specific tag is how showback and chargeback are done.
- `--compartment-depth` (FLOAT), `--filter` (JSON), `--is-aggregate-by-time`, `--page`,
  `--limit` refine the rest [verified, help].

Rows come back under **`data.items`**, not `data` — a `--query` written against `data[]` returns
nothing and reads like a zero bill.

## 2. Forecast

`--forecast` takes JSON: `{"forecastType":"BASIC","timeForecastEnded":"2026-11-01T00:00:00Z"}`.
Forecast rows arrive in the same `data.items`, flagged `is-forecast: true`
[verified, executed 2026-09-09 with `--granularity MONTHLY` over 2026-07-01..2026-09-01].

Use UTC midnight, including zero fractional seconds. A `DAILY` forecast with a nonzero
time-of-day returned
`InvalidParameter` / `Forecasting invalid date range: Passed UTC date does not have the right
precision: hours, minutes, seconds, and second fractions must be 0`, status 400, for both
`timeForecastEnded` alone and the `timeForecastStarted`+`timeForecastEnded` pair
[verified, reproduced 2026-09-09]. Zero the time-of-day; mid-month midnight is valid for DAILY forecasts.
A date-only forecast value fails earlier, in the CLI, with `Unable to process JSON input`
[verified].

## 3. Scope, policy and throttling

`--tenant-id` is the **tenancy** OCID. A child compartment is legal and simply narrows the
answer, so a zero total is far more often the wrong scope than a zero bill.

Policy: `Allow group <g> to read usage-report in tenancy`, plus `read usage-budgets` for budgets
[verified, research/04b §19]. Without it, reads answer
`Authorization failed or requested resource not found.` with status 404 — the deliberately
ambiguous NAONF envelope, which leaves scope, access and resource existence unresolved. `budgets cost-ad
cost-anomaly-monitor-collection list-monitors` returned exactly that in this tenancy
[verified, executed 2026-09-09].

[unverified] `HOURLY` over a long window is the usual way to earn `User-rate limit exceeded`, 429. Widen the
granularity rather than retrying; the answer does not get finer by asking harder.

## 4. Siblings under the same group

`query` and `custom-table` hold saved Cost Analysis views (`usage-api query list --compartment-id
<t> --limit 10` returned `[]` here [verified, executed]). `schedule`, `scheduled-run` and
`email-recipients-group` drive scheduled CSV delivery to a bucket (`schedule list` returned `[]`
[verified, executed]). `usage-carbon-emission-summary`, `usage-carbon-emissions-query`,
`average-carbon-emission` and `clean-energy-usage` cover sustainability reporting
[verified, help].

**`oci usage` is a different service.** The Usage Proxy carries `rewards` (monthly Oracle
Support Rewards), `usagelimits` and `resources`; its reward reads need `--subscription-id` and
`--tenancy-id` together [verified, help]. Reaching for `oci usage` when the question is "what did
we spend" is the common wrong turn.

## 5. Reads

```bash
oci usage-api query list --compartment-id "$TENANCY_ID" --limit 20 --query 'data.items[].["display-name",id]' --profile "$PROFILE" --region "$REGION"
```

```bash
oci usage-api schedule list --compartment-id "$TENANCY_ID" --limit 20 --query 'data.items[].[name,"output-file-format"]' --profile "$PROFILE" --region "$REGION"
```

Docs (HTTP 200, 2026-09-09):
https://docs.oracle.com/en-us/iaas/Content/Billing/Concepts/costanalysisoverview.htm ·
https://docs.oracle.com/en-us/iaas/api/#/en/usage/20200107/
