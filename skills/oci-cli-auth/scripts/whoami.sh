#!/usr/bin/env bash
# There is no `oci whoami`. This composes the four probes that answer it, cheapest first:
# the profile read offline, then the user behind the profile, then home region and
# subscriptions, then direct child compartments. Every call goes through oci_ro.
set -euo pipefail

usage() {
  cat <<'USAGE'
whoami.sh [--profile NAME] [--region ID] [--config PATH] [--include-subtree]

Establishes identity BEFORE any other OCI call. Prints one JSON object:
  {profile, config, auth_hint, user_ocid, tenancy_ocid, region, identity,
   subscriptions, compartments}
`auth_hint` is read from the profile, not asserted: a section carrying
security_token_file and no user is a session profile; neither key present means an
instance or resource principal, and `identity` will be null by design.
An explicit --profile or OCI_CLI_PROFILE is required. Missing config exits 2;
unreachable probes come back null. Lists direct children by default;
--include-subtree explicitly requests descendants and may be refused by scope policy.
USAGE
}

profile="${OCI_CLI_PROFILE:-}"
config="${OCI_CLI_CONFIG_FILE:-$HOME/.oci/config}"
region=""
subtree=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile) profile="$2"; shift 2 ;;
    --region) region="$2"; shift 2 ;;
    --config) config="$2"; shift 2 ;;
    --include-subtree) subtree=true; shift ;;
    --help|-h) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done

root="${CLAUDE_PLUGIN_ROOT:-}"
if [[ -z "$root" ]]; then
  root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
  while [[ "$root" != "/" && ! -f "$root/scripts/lib/oci_ro.sh" ]]; do
    root="$(dirname -- "$root")"
  done
fi
# shellcheck source=/dev/null
. "$root/scripts/lib/oci_ro.sh"

# Offline: read only the requested section of the config file. No secrets are printed.
field() {
  awk -v section="[$profile]" -v key="$1" '
    /^\[/ { inside = ($0 == section); next }
    inside && $0 ~ "^[ \t]*" key "[ \t]*=" { sub(/^[^=]*=[ \t]*/, ""); gsub(/[ \t\r]/, ""); print; exit }
  ' "$config" 2>/dev/null || true
}

[[ -n "$profile" ]] || { echo '{"error":"profile_required"}'; exit 2; }
[[ -f "$config" ]] || { echo '{"error":"config_missing"}'; exit 2; }
user="$(field user)"
tenancy="$(field tenancy)"
region="${region:-${OCI_CLI_REGION:-$(field region)}}"
token="$(field security_token_file)"
key="$(field key_file)"

auth_hint="unknown"
if [[ -n "$token" && -z "$user" ]]; then auth_hint="security_token"
elif [[ -n "$user" && -n "$key" ]]; then auth_hint="api_key"
elif [[ -z "$user" && -z "$key" ]]; then auth_hint="instance_or_resource_principal"
fi

probe() { oci_ro --sanitize -- "$@" --profile "$profile" --config-file "$config" ${region:+--region "$region"} || echo null; }

identity=null
if [[ -n "$user" ]]; then
  identity="$(probe iam user get --user-id "$user" \
    --query 'data.{name:name,mfa:"is-mfa-activated",state:"lifecycle-state"}')"
fi
subscriptions=null
if [[ -n "$tenancy" ]]; then
  subscriptions="$(probe iam region-subscription list --tenancy-id "$tenancy" \
    --query 'data[].{region:"region-name",key:"region-key",home:"is-home-region"}')"
  compartments="$(probe iam compartment list --compartment-id "$tenancy" \
    --compartment-id-in-subtree "$subtree" --access-level ANY --limit 100 \
    --query 'data[].{name:name,state:"lifecycle-state"}')"
else
  compartments=null
fi

python3 - "$profile" "$config" "$auth_hint" "$user" "$tenancy" "$region" \
  "$identity" "$subscriptions" "${compartments:-null}" <<'PY'
import json, sys
p, cfg, hint, user, tenancy, region, ident, subs, comps = sys.argv[1:10]
def blob(text):
    """Unwrap the oci_ro envelope to its items; a refusal or failure becomes null."""
    try:
        result = json.loads(text)
    except ValueError:
        return None
    if not isinstance(result, dict) or not result.get("ok"):
        return None
    return (result.get("data") or {}).get("items")
def short(ocid):
    return "<redacted>" if ocid else None
print(json.dumps({"profile": p, "config": cfg, "auth_hint": hint,
                  "user_ocid": short(user), "tenancy_ocid": short(tenancy),
                  "region": region or None, "identity": blob(ident),
                  "subscriptions": blob(subs), "compartments": blob(comps)},
                 indent=2, sort_keys=True))
PY
