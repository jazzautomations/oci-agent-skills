#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "--help" ]]; then
  printf "%s\n" 'Set PROFILE REGION COMPARTMENT_ID SHAPE; returns newest compatible Oracle Linux 9 image.'
  exit 0
fi
LIB="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../scripts/lib" && pwd)"
. "$LIB/oci_ro.sh"
: "${PROFILE:?Set PROFILE explicitly}"
: "${REGION:?Set REGION explicitly}"
: "${COMPARTMENT_ID:?Set COMPARTMENT_ID explicitly}"
: "${SHAPE:?Set SHAPE explicitly}"
oci_ro -- compute image list --compartment-id "$COMPARTMENT_ID" --operating-system "Oracle Linux" --operating-system-version "9" --shape "$SHAPE" --sort-by TIMECREATED --sort-order DESC --limit 1 --query 'data[].{id:id,name:"display-name"}' --profile "$PROFILE" --region "$REGION"
