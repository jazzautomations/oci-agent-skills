#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "--help" ]]; then
  printf "%s\n" 'Set PROFILE REGION TENANCY_ID PRIOR_START PRIOR_END CURRENT_START CURRENT_END (YYYY-MM-DD, UTC).'
  printf "%s\n" 'Prints two MONTHLY cost-by-service reads, prior window then current, for local diffing.'
  printf "%s\n" 'Figures are the tenancy rate card, not list price. Rows arrive under data.items.'
  exit 0
fi
LIB="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../scripts/lib" && pwd)"
. "$LIB/oci_ro.sh"
: "${PROFILE:?Set PROFILE explicitly}"
: "${REGION:?Set REGION explicitly}"
: "${TENANCY_ID:?Set TENANCY_ID explicitly (usage-api takes the tenancy, not a child compartment)}"
: "${PRIOR_START:?Set PRIOR_START explicitly}"
: "${PRIOR_END:?Set PRIOR_END explicitly}"
: "${CURRENT_START:?Set CURRENT_START explicitly}"
: "${CURRENT_END:?Set CURRENT_END explicitly}"
for WINDOW in "$PRIOR_START $PRIOR_END" "$CURRENT_START $CURRENT_END"; do
  set -- $WINDOW
  oci_ro -- usage-api usage-summary request-summarized-usages --tenant-id "$TENANCY_ID" --time-usage-started "$1" --time-usage-ended "$2" --granularity MONTHLY --query-type COST --group-by '["service"]' --limit 100 --query 'data.items[].[service,"computed-amount",currency]' --profile "$PROFILE" --region "$REGION"
done
