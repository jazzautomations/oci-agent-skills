# Public list prices and graduated bands

Use `scripts/price.sh B91628 USD --quantity 100 --cache .local/prices-usd.json`.
The credential-free endpoint is https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/ .
Only `currencyCode` and `partNumber` are supported query filters. Fetch once; filter locally.

The helper reports all PAY_AS_YOU_GO bands, snapshot, currency, marginal rate and graduated cost.
It selects the band containing quantity in `[rangeMin, rangeMax)`. **Never use `prices[0]`**:
50 SKUs in the 2026-09-09 snapshot start with a free band before a paid band.

| SKU | Quantity | Marginal USD rate | Graduated USD cost |
|---|---:|---:|---:|
| B91628 Object Storage | 100 GB-month | 0.0255 | 2.295 |
| B93030 Flexible LB base | 1488 LB-hours | 0.0113 | 8.4072 |
| B91961 Block Volume | 100 GB-month | 0.0255 | 2.55 |

Rechecked against the live API 2026-09-10; snapshot 2026-09-09T16:34:38.537Z.
Free allowances apply once per tenancy/month. Avoided cost is cost(total) minus
cost(total - removed), **not** rate times removed and not a new free allowance per resource.
B93030 does not price Network Load Balancers. Missing SKUs, currencies and ranges are unknown,
never zero. Cache dates are always printed; an explicit cached snapshot is not refreshed silently.

Use the metric's units: storage GB-month, compute OCPU-hour and memory GB-hour.
Most x86 OCPUs have two vCPUs; Ampere OCPUs have one. State hours/month explicitly.
Block-volume performance is additive: capacity B91961 plus GB × VPU × B91962.

Label every figure **list price, pre-discount**, with snapshot and currency. No Rate Card,
Universal Credits, Support Rewards or FX is applied. Contract costs come from Usage API.
Resource free-tier eligibility and shared allowances must be established before claiming savings.

Sources (read 2026-09-10): https://www.oracle.com/cloud/price-list/ and
https://www.oracle.com/cloud/costestimator.html .

| Failure signal | Action |
|---|---|
| Missing price or currency | Report unknown; never substitute zero. |
| Incomplete page or 429 | Narrow scope and retry at most three times. |
