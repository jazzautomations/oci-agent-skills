#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/../.." && pwd)"
OUT="${1:-$ROOT/.local/migration-demo}"
mkdir -p "$OUT"
python3 "$ROOT/skills/oci-migration-assess/scripts/inventory_normalize.py" "$ROOT/skills/oci-migration-assess/fixtures/aws-sample.json" --out "$OUT/inventory.json"
python3 "$ROOT/skills/oci-migration-map/scripts/map_and_price.py" "$OUT/inventory.json" --price-cache "$OUT/prices.json" --live-source-prices --out "$OUT/report.md" --json-out "$OUT/report.json"
python3 "$ROOT/skills/oci-migration-landing-zone/scripts/emit_tfvars.py" "$OUT/inventory.json" --region us-ashburn-1 --service-label migdemo --target-cidr 10.80.0.0/16 --out-dir "$OUT/landing-zone"
printf 'Demo complete. Report: %s/report.md\n' "$OUT"
