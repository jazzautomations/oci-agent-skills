#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "--help" ]]; then
  printf "%s\n" 'Set PROFILE REGION COMPARTMENT_ID TENANCY_ID; reads limits, cluster versions and worker options.'
  exit 0
fi
LIB="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../scripts/lib" && pwd)"
. "$LIB/oci_ro.sh"
: "${PROFILE:?Set PROFILE explicitly}"
: "${REGION:?Set REGION explicitly}"
: "${COMPARTMENT_ID:?Set COMPARTMENT_ID explicitly}"
: "${TENANCY_ID:?Set TENANCY_ID explicitly}"
oci_ro -- limits value list --compartment-id "$TENANCY_ID" --service-name container-engine --limit 20 --query 'data[].{name:name,value:value}' --profile "$PROFILE" --region "$REGION"
oci_ro -- ce cluster-options get --cluster-option-id all --query 'data."kubernetes-versions"' --profile "$PROFILE" --region "$REGION"
oci_ro -- ce node-pool-options get --node-pool-option-id all --query 'data.{shapes:shapes,sources:sources}' --profile "$PROFILE" --region "$REGION"
