#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "--help" ]]; then
  printf "%s\n" 'Set PROFILE REGION COMPARTMENT_ID BASTION_ID SESSION_ID; inspects access/session metadata, never creates or connects.'
  exit 0
fi
LIB="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../scripts/lib" && pwd)"
. "$LIB/oci_ro.sh"
: "${PROFILE:?Set PROFILE explicitly}"
: "${REGION:?Set REGION explicitly}"
: "${COMPARTMENT_ID:?Set COMPARTMENT_ID explicitly}"
: "${BASTION_ID:?Set BASTION_ID explicitly}"
: "${SESSION_ID:?Set SESSION_ID explicitly}"
oci_ro -- bastion bastion get --bastion-id "$BASTION_ID" --query 'data.{subnet:"target-subnet-id",allowed:"client-cidr-block-allow-list",state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
oci_ro -- bastion session get --session-id "$SESSION_ID" --query 'data.{id:id,state:"lifecycle-state",ttl:"session-ttl-in-seconds"}' --profile "$PROFILE" --region "$REGION"
