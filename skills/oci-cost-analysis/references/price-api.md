Purpose: price a resource before it exists, with no tenancy and no credentials.
Source: research/06c §8, research/04b §21; verified live 2026-09-08 and re-probed 2026-09-09.

## 1. The endpoint

`https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/`

It is the backing API of the Oracle Cloud Cost Estimator and is fully public: no auth, no API
key, no tenancy, no request signing [verified]. That makes it the right tool for "how much would
X cost" and the wrong tool for "what did I spend" — it cannot see a tenancy at all.

## 2. The two rules that matter

**Only `currencyCode` and `partNumber` are valid query parameters, and the trailing `/` before
`?` is required.** Anything else returns HTTP 400, not a silent ignore: `?limit=3` answered
`400` again on 2026-09-09 [verified, re-probed]. There is no server-side text or category
search — `?serviceCategory=Compute` returns the whole unfiltered catalogue [verified].

**Download once, filter locally.** The bare catalogue is ~2.85 MB across 627 products and 110
service categories; `?currencyCode=USD` returns ~189 KB, about 15x smaller [verified].
`partNumber` is repeatable but unreliable past roughly two values — a nine-part request returned
only the first item [verified]. Loop instead of building a query-string DSL.

## 3. Three working calls

```bash
curl -sS 'https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/?partNumber=B93113&currencyCode=USD' \
  | jq -r '.items[] | [.partNumber, .displayName, .metricName, .currencyCodeLocalizations[0].prices[0].value] | @tsv'
```

Re-run 2026-09-09, unchanged [verified]:
`B93113  Compute - Standard - E4 - OCPU  OCPU Per Hour   0.025`

```bash
curl -sS 'https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/?currencyCode=USD' -o /tmp/oci_usd.json
jq -r '.items[] | select(.displayName | test("Block Volume|Object Storage - Storage"; "i"))
  | [ .partNumber, .displayName,
      ([ .currencyCodeLocalizations[0].prices[] | "\(.value)@[\(.rangeMin // "-")..\(.rangeMax // "-")]" ] | join(" | ")) ]
  | @tsv' /tmp/oci_usd.json
```

```bash
curl -sS 'https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/?currencyCode=USD' \
  | jq -r '(.items[] | select(.partNumber=="B97384") | .currencyCodeLocalizations[0].prices[0].value) as $ocpu
    | (.items[] | select(.partNumber=="B97385") | .currencyCodeLocalizations[0].prices[0].value) as $mem
    | "E5 2 OCPU + 16 GB, 730h = USD \((($ocpu*2)+($mem*16))*730 | .*100|round/100)"'
```

`scripts/price.sh` wraps the first form.

## 4. Reading the payload honestly

- `lastUpdated` is the snapshot date; it was `2026-09-01T14:26:53.943Z` on 2026-09-09
  [verified]. Quote it beside every figure.
- Prices are **tiered**: each entry carries `rangeMin`/`rangeMax`, and a free allowance appears
  as a `value: 0` range — the Always Free A1 allotment is literally the first tier of the paid
  SKU. Apply tiers **per tenancy per month**, not per resource.
- `model` is `PAY_AS_YOU_GO` only. No commit, no Universal Credits, no Rate Card, no Support
  Rewards, and no per-region axis — Oracle prices commercial regions uniformly. Label output
  "list price, pre-discount"; the tenancy's real rates come from the Usage API.
- Currencies include AED, ARS, AUD, BHD, BRL, CAD ... USD [verified].

## 5. Estimating method

1. Fetch `?currencyCode=<ISO>` once per session and cache it.
2. Resolve each resource to a part number by `displayName` regex — never hard-code a price.
3. Apply the tiers, tenancy-wide and monthly. Oracle's own convention is **730 hours/month**:
   `line_cost = unit_price x quantity x 730`.
4. Never present a single number. Present the subtotal **plus the step-function deltas**,
   because OCI's bill shocks are discrete, not gradual.

Docs (HTTP 200, 2026-09-09): https://www.oracle.com/cloud/price-list/ ·
https://www.oracle.com/cloud/costestimator.html
