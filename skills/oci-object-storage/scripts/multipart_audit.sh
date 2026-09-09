#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "--help" ]]; then
  printf "%s\n" 'Set PROFILE REGION COMPARTMENT_ID NAMESPACE BUCKET; emits a bounded upload sample, never aborts.'
  exit 0
fi
LIB="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../scripts/lib" && pwd)"
. "$LIB/oci_ro.sh"
: "${PROFILE:?Set PROFILE explicitly}"
: "${REGION:?Set REGION explicitly}"
: "${COMPARTMENT_ID:?Set COMPARTMENT_ID explicitly}"
: "${NAMESPACE:?Set NAMESPACE explicitly}"
: "${BUCKET:?Set BUCKET explicitly}"
oci_ro -- os multipart list --namespace-name "$NAMESPACE" --bucket-name "$BUCKET" --limit 20 --query 'data[].{object:object,id:"upload-id",created:"time-created"}' --profile "$PROFILE" --region "$REGION"
