#!/usr/bin/env bash
# Source and call oci_ro, or execute this file with OCI argv. Never eval argv.
oci_ro() {
  local oci_ro_dir
  oci_ro_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
  python3 "${oci_ro_dir}/oci_ro.py" "$@"
}
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  oci_ro "$@"
fi
