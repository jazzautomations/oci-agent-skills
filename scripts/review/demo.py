#!/usr/bin/env python3
"""Recorded offline component walkthrough; no model calls or OCI service operations."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]


def execute(argv, environment, *, payload=None, expected_code=0):
    result = subprocess.run(argv, cwd=ROOT, env=environment,
                            input=json.dumps(payload) if payload is not None else None,
                            capture_output=True, text=True, timeout=60)
    if result.returncode != expected_code:
        raise ValueError("Demo component returned an unexpected exit code")
    return json.loads(result.stdout)


def run():
    with tempfile.TemporaryDirectory(prefix="oci-review-demo-") as directory:
        environment = {k: v for k, v in os.environ.items() if not k.startswith("OCI_")}
        environment.update(OCI_CONFIG_FILE=str(Path(directory) / "absent"),
                           OCI_CLI_CONFIG_FILE=str(Path(directory) / "absent"))
        catalog = execute([sys.executable, str(ROOT / "scripts/catalog.py"), "required",
                           "compute instance list", "--json"], environment)
        assert catalog["ok"] and catalog["items"][0]["path"] == "compute instance list"
        assert "--compartment-id" in catalog["items"][0]["required"]
        guard = [sys.executable, str(ROOT / "scripts/guard_oci.py"), "--stdin-argv"]
        reads = execute(guard, environment, payload=["oci", "compute", "instance", "list"])
        writes = execute(guard, environment, payload=["oci", "compute", "instance", "launch"])
        read_decision = reads["hookSpecificOutput"]["permissionDecision"]
        write_decision = writes["hookSpecificOutput"]["permissionDecision"]
        assert read_decision == "allow" and write_decision == "ask"
        mcp = execute([sys.executable, "-m", "oci_readonly.smoke", "--region", "us-chicago-1"],
                      environment)
        assert mcp["ok"] and not mcp["live"] and mcp["tool_count"] == 15
    paths = ["scripts/review/demo.py", "scripts/catalog.py", "scripts/guard_oci.py",
             "scripts/guard_lib.py", "catalog/cli.jsonl", "catalog/guard.json",
             "catalog/scripts.json", "runtime/oci_readonly/server.py",
             "runtime/oci_readonly/smoke.py", "runtime/uv.lock"]
    return {
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "offline_component_walkthrough", "ok": True,
        "scope": "Catalog lookup, inert argv classification and MCP stdio discovery/invalid-scope rejection. No agent task, OCI operation or host permission enforcement was measured.",
        "credentials": "OCI environment selectors removed; both config paths point to an absent file.",
        "checks": [
            {"name": "catalog_required_scope", "ok": True, "result": catalog},
            {"name": "read_classification", "ok": True, "decision": read_decision},
            {"name": "write_requires_review", "ok": True, "decision": write_decision,
             "executed": False},
            {"name": "mcp_stdio", "ok": True, "result": mcp},
        ],
        "inputs_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                          for name in paths},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="Optional JSON output; stdout is always JSON")
    args = parser.parse_args()
    try:
        report = run()
    except (OSError, ValueError, KeyError, AssertionError, subprocess.TimeoutExpired):
        print(json.dumps({"ok": False, "error": "component_check_failed",
                          "hint": "Use the locked runtime; inspect components separately. Raw output suppressed."}))
        return 1
    rendered = json.dumps(report, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered)
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
