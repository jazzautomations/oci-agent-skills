#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "--help" ]]; then
  printf "%s\n" 'Set PROFILE REGION COMPARTMENT_ID TENANCY_ID AD LIMIT_NAME; checks limits, not physical hosts.'
  exit 0
fi
LIB="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../scripts/lib" && pwd)"
. "$LIB/oci_ro.sh"
: "${PROFILE:?Set PROFILE explicitly}"
: "${REGION:?Set REGION explicitly}"
: "${COMPARTMENT_ID:?Set COMPARTMENT_ID explicitly}"
: "${TENANCY_ID:?Set TENANCY_ID explicitly}"
: "${AD:?Set AD explicitly}"
: "${LIMIT_NAME:?Set LIMIT_NAME explicitly}"
oci_ro -- limits value list --compartment-id "$TENANCY_ID" --service-name compute --limit 20 --query 'data[].{name:name,value:value,ad:"availability-domain"}' --profile "$PROFILE" --region "$REGION"
oci_ro -- limits resource-availability get --compartment-id "$COMPARTMENT_ID" --service-name compute --limit-name "$LIMIT_NAME" --availability-domain "$AD" --query 'data.{available:available,used:used}' --profile "$PROFILE" --region "$REGION"
