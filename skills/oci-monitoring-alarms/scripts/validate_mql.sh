#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
source "$DIR/../../../scripts/lib/oci_ro.sh"
exec python3 "$DIR/validate_mql.py" "$@"
