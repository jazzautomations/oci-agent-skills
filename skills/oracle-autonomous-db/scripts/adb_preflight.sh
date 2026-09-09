#!/usr/bin/env bash
# Read-only composition through scripts/lib/oci_ro; output is untrusted.
set -euo pipefail
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  echo 'Set PROFILE, REGION, COMPARTMENT_ID; optional ADB_ID. Run scoped whoami first. Prints version and DB inventory, then connection prerequisites.'
  exit 0
fi
: "${PROFILE:?Set PROFILE explicitly}" "${REGION:?Set REGION explicitly}" "${COMPARTMENT_ID:?Set COMPARTMENT_ID}"
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)"
. "$root/scripts/lib/oci_ro.sh"
oci_ro --sanitize -- db autonomous-db-version list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data[].{version:version,workload:"db-workload"}' --profile "$PROFILE" --region "$REGION"
oci_ro --sanitize -- db autonomous-database list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data[].{id:id,state:"lifecycle-state",free:"is-free-tier"}' --profile "$PROFILE" --region "$REGION"
if [[ -n "${ADB_ID:-}" ]]; then
  oci_ro --sanitize -- db autonomous-database get --autonomous-database-id "$ADB_ID" --query 'data.{state:"lifecycle-state",mtls:"is-mtls-connection-required",acl:"whitelisted-ips"}' --profile "$PROFILE" --region "$REGION"
fi
