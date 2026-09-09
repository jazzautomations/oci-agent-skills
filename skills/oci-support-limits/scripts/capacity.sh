#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "--help" ]]; then
  printf "%s\n" 'Set PROFILE REGION TENANCY_ID SERVICE LIMIT_NAME; AD is required only for AD-scoped limits. Reads scope-type, configured value and headroom. Limits are not physical capacity.'
  exit 0
fi
LIB="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../scripts/lib" && pwd)"
. "$LIB/oci_ro.sh"
: "${PROFILE:?Set PROFILE explicitly}"
: "${REGION:?Set REGION explicitly}"
: "${TENANCY_ID:?Set TENANCY_ID explicitly (limits take the tenancy, not a child compartment)}"
: "${SERVICE:?Set SERVICE explicitly}"
: "${LIMIT_NAME:?Set LIMIT_NAME explicitly}"
AD_FLAG=()
[[ -z "${AD:-}" ]] || AD_FLAG=(--availability-domain "$AD")
oci_ro -- limits definition list --compartment-id "$TENANCY_ID" --service-name "$SERVICE" --limit 50 --query 'data[].{n:name,scope:"scope-type",dyn:"is-dynamic"}' --profile "$PROFILE" --region "$REGION"
oci_ro -- limits value list --compartment-id "$TENANCY_ID" --service-name "$SERVICE" --limit 50 --query 'data[].{n:name,v:value,ad:"availability-domain"}' --profile "$PROFILE" --region "$REGION"
oci_ro -- limits resource-availability get --compartment-id "$TENANCY_ID" --service-name "$SERVICE" --limit-name "$LIMIT_NAME" "${AD_FLAG[@]}" --query 'data' --profile "$PROFILE" --region "$REGION"
