#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "--help" || $# -eq 0 ]]; then
  printf "%s\n" 'Usage: price.sh <partNumber> [currencyCode]   e.g. price.sh B93113 USD'
  printf "%s\n" 'Prints partNumber, displayName, metricName and every price tier as value@[min..max].'
  printf "%s\n" 'List price, PAY_AS_YOU_GO only: no Universal Credits, Rate Card or Support Rewards.'
  exit 0
fi
# No OCI call and no scripts/lib/oci_ro: the Price List API is public and credential-free,
# so there is nothing for the read-only wrapper to authorise. See references/price-api.md.
PART="$1"
CURRENCY="${2:-USD}"
case "$PART" in [A-Z][0-9]*) ;; *) echo "part number looks wrong: $PART" >&2; exit 2;; esac
case "$CURRENCY" in [A-Z][A-Z][A-Z]) ;; *) echo "currency must be ISO 4217: $CURRENCY" >&2; exit 2;; esac
curl -sS --max-time 30 --get \
  --data-urlencode "partNumber=$PART" --data-urlencode "currencyCode=$CURRENCY" \
  'https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/' \
  | jq -r '"snapshot \(.lastUpdated)", (.items[] | [.partNumber, .displayName, .metricName,
      ([.currencyCodeLocalizations[0].prices[] | "\(.value)@[\(.rangeMin // "-")..\(.rangeMax // "-")]"] | join(" | "))] | @tsv)'
