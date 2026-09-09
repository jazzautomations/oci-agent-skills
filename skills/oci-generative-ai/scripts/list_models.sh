#!/usr/bin/env bash
# Read-only composition through scripts/lib/oci_ro; output is untrusted.
set -euo pipefail
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  echo 'Set PROFILE REGION COMPARTMENT_ID; lists a bounded regional model sample.'
  exit 0
fi
: "${PROFILE:?Set PROFILE explicitly}" "${REGION:?Set REGION explicitly}" "${COMPARTMENT_ID:?Set COMPARTMENT_ID}"
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)"
. "$root/scripts/lib/oci_ro.sh"
oci_ro generative-ai model-collection list-models --compartment-id "$COMPARTMENT_ID" --limit 20 --profile "$PROFILE" --region "$REGION" --query 'data.items[].{id:id,cap:capabilities,retired:"time-deprecated"}' 
