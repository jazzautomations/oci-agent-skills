#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "--help" ]]; then
  printf "%s\n" 'Set PROFILE REGION COMPARTMENT_ID APPLICATION_ID; reads application/function metadata and available Container Instance shapes.'
  exit 0
fi
LIB="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../scripts/lib" && pwd)"
. "$LIB/oci_ro.sh"
: "${PROFILE:?Set PROFILE explicitly}"
: "${REGION:?Set REGION explicitly}"
: "${COMPARTMENT_ID:?Set COMPARTMENT_ID explicitly}"
: "${APPLICATION_ID:?Set APPLICATION_ID explicitly}"
oci_ro -- fn application list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data[].{id:id,architecture:shape,subnets:"subnet-ids"}' --profile "$PROFILE" --region "$REGION"
oci_ro -- fn function list --application-id "$APPLICATION_ID" --limit 20 --query 'data[].{id:id,memory:"memory-in-mbs",timeout:"timeout-in-seconds",digest:"image-digest"}' --profile "$PROFILE" --region "$REGION"
oci_ro -- container-instances container-instance list-shapes --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data.items[].{name:name,ocpus:"ocpu-options",memory:"memory-options"}' --profile "$PROFILE" --region "$REGION"
