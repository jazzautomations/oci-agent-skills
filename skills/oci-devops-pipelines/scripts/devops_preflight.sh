#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "--help" ]]; then
  printf "%s\n" 'Set PROFILE REGION COMPARTMENT_ID PROJECT_ID; reads project pipelines and repository metadata.'
  exit 0
fi
LIB="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../scripts/lib" && pwd)"
. "$LIB/oci_ro.sh"
: "${PROFILE:?Set PROFILE explicitly}"
: "${REGION:?Set REGION explicitly}"
: "${COMPARTMENT_ID:?Set COMPARTMENT_ID explicitly}"
: "${PROJECT_ID:?Set PROJECT_ID explicitly}"
oci_ro -- devops project list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data.items[].{id:id,name:name,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
oci_ro -- devops build-pipeline list --project-id "$PROJECT_ID" --limit 20 --query 'data.items[].{id:id,name:"display-name"}' --profile "$PROFILE" --region "$REGION"
oci_ro -- artifacts container repository list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data.items[].{id:id,name:"display-name",public:"is-public"}' --profile "$PROFILE" --region "$REGION"
