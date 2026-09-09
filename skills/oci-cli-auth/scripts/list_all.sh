#!/usr/bin/env bash
# Run one OCI list leaf and say honestly whether the answer is complete.
# The CLI's truncation warning goes to stderr and the exit status stays 0, so a
# stdout-only reader silently under-reports. This asks the catalog whether the leaf
# supports --all, uses it when it does, and labels the result either way.
set -euo pipefail

usage() {
  cat <<'USAGE'
list_all.sh <leaf> [oci flags...]

  <leaf>  the command path with the CLI name stripped, quoted as one word,
          e.g. "iam compartment list" or "compute instance list"

Prints {leaf, mode, complete, count, warning, items}.
  mode "all"     the leaf supports --all; every page was fetched
  mode "bounded" the leaf has no --all; the wrapper's page bound applies
  complete       false whenever a bound or a truncation warning was seen
Read-only: refuses any leaf the catalog does not mark read-only.
USAGE
}

[[ $# -ge 1 ]] || { usage >&2; exit 2; }
case "$1" in --help|-h) usage; exit 0 ;; esac
leaf="$1"; shift

root="${CLAUDE_PLUGIN_ROOT:-}"
if [[ -z "$root" ]]; then
  root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
  while [[ "$root" != "/" && ! -f "$root/scripts/lib/oci_ro.sh" ]]; do
    root="$(dirname -- "$root")"
  done
fi
# shellcheck source=/dev/null
. "$root/scripts/lib/oci_ro.sh"

# Offline catalog lookup: is the leaf read-only, and does it expose --all?
support="$(python3 - "$root/catalog/cli.jsonl" "$leaf" <<'PY'
import json, sys
for line in open(sys.argv[1], encoding="utf-8"):
    row = json.loads(line)
    if row.get("path") == sys.argv[2]:
        print(json.dumps({"known": True, "read_only": bool(row.get("read_only")),
                          "all": "--all" in row.get("flags", [])}))
        break
else:
    print(json.dumps({"known": False, "read_only": False, "all": False}))
PY
)"
case "$support" in
  *'"known": false'*) echo '{"error":"unknown_leaf"}' >&2; exit 2 ;;
  *'"read_only": false'*) echo '{"error":"not_read_only"}' >&2; exit 3 ;;
esac

mode="bounded"
declare -a page=()
if [[ "$support" == *'"all": true'* ]]; then
  mode="all"
  page=(--all)
  export OCI_RO_ALLOW_ALL=1
fi

warn="$(mktemp)"; body="$(mktemp)"
trap 'rm -f "$warn" "$body"' EXIT
# shellcheck disable=SC2086
status=0
oci_ro --sanitize -- $leaf "${page[@]}" "$@" >"$body" 2>"$warn" || status=$?

python3 - "$leaf" "$mode" "$warn" "$body" <<'PY'
import json, sys
leaf, mode, warn_path, body_path = sys.argv[1:5]
warning = "not all resources were returned" in open(warn_path, encoding="utf-8", errors="replace").read()
try:
    result = json.loads(open(body_path, encoding="utf-8").read())
except ValueError:
    result = {}
items = (result.get("data") or {}).get("items") if result.get("ok") else None
rows = items.get("data") if isinstance(items, dict) else items
count = len(rows) if isinstance(rows, list) else None
print(json.dumps({"leaf": leaf, "mode": mode,
                  "complete": bool(result.get("ok")) and mode == "all" and not warning and not result.get("truncated"),
                  "count": count, "warning": warning, "items": rows},
                 indent=2, sort_keys=True))
PY

exit "$status"
