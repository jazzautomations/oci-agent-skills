#!/usr/bin/env bash
# MUTATING — not run in this repo; defaults to a local dry-run.
set -euo pipefail
DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$DIR/control.py" provision "$@"
