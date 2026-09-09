#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "--help" ]]; then
  printf "%s\n" 'Set PROFILE REGION TENANCY_ID AD LIMIT_NAME; reads home region, the Always Free allotment, its scope-type, headroom (negative = already over), and whether the shape is offered. Entitlement is not capacity, and a limit is not an offer.'
  exit 0
fi
LIB="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../scripts/lib" && pwd)"
. "$LIB/oci_ro.sh"
: "${PROFILE:?Set PROFILE explicitly}"
: "${REGION:?Set REGION explicitly}"
: "${TENANCY_ID:?Set TENANCY_ID explicitly (limits take the tenancy, not a child compartment)}"
: "${AD:?Set AD explicitly; free compute limits are AD-scoped}"
: "${LIMIT_NAME:=standard-a1-core-count}"
oci_ro -- iam region-subscription list --tenancy-id "$TENANCY_ID" --query 'data[?"is-home-region"].{r:"region-name",s:status}' --profile "$PROFILE" --region "$REGION"
oci_ro -- limits value list --compartment-id "$TENANCY_ID" --service-name compute --name "$LIMIT_NAME" --limit 100 --query 'data[].{n:name,v:value,ad:"availability-domain"}' --profile "$PROFILE" --region "$REGION"
oci_ro -- limits definition list --compartment-id "$TENANCY_ID" --service-name compute --name "$LIMIT_NAME" --limit 10 --query 'data[].{n:name,scope:"scope-type",dyn:"is-dynamic"}' --profile "$PROFILE" --region "$REGION"
oci_ro -- limits resource-availability get --compartment-id "$TENANCY_ID" --service-name compute --limit-name "$LIMIT_NAME" --availability-domain "$AD" --query 'data.{used:used,available:available,quota:"effective-quota-value"}' --profile "$PROFILE" --region "$REGION"
oci_ro -- compute shape list --compartment-id "$TENANCY_ID" --availability-domain "$AD" --limit 100 --query 'data[?contains(shape,`A1`)||contains(shape,`Micro`)].shape' --profile "$PROFILE" --region "$REGION"
