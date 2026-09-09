#!/usr/bin/env bash
set -euo pipefail
# triage.py routes all OCI calls through scripts/lib/oci_ro.py.
DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
exec python3 "$DIR/triage.py" "$@"
