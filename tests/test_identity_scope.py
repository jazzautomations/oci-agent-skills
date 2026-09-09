"""Identity diagnostics must stay inside their declared scope by default."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("subtree", [False, True])
def test_whoami_respects_bounded_smoke_scope(tmp_path, subtree):
    config = tmp_path / "config"
    config.write_text("[TEST]\nuser=example-user\ntenancy=example-tenancy\nregion=us-test-1\nkey_file=example-key\n")
    capture = tmp_path / "argv.jsonl"
    executable = tmp_path / "oci"
    executable.write_text(
        f"#!{sys.executable}\nimport json, sys\n"
        f"with open({str(capture)!r}, 'a') as stream: stream.write(json.dumps(sys.argv[1:])+'\\n')\n"
        "print('[]')\n"
    )
    executable.chmod(0o755)
    environment = dict(os.environ, PATH=str(tmp_path) + os.pathsep + os.environ["PATH"],
                       CLAUDE_PLUGIN_ROOT=str(ROOT), OCI_RO_SMOKE_SCOPE="example-tenancy",
                       OCI_RO_SMOKE_PROFILE="TEST", OCI_RO_SMOKE_REGION="us-test-1")
    result = subprocess.run(
        ["bash", str(ROOT / "skills/oci-cli-auth/scripts/whoami.sh"), "--profile", "TEST",
         "--region", "us-test-1", "--config", str(config), *(["--include-subtree"] if subtree else [])],
        env=environment, capture_output=True, text=True, check=True,
    )
    report = json.loads(result.stdout)
    calls = [json.loads(line) for line in capture.read_text().splitlines()]
    assert report["compartments"] == (None if subtree else [])
    assert len(calls) == (2 if subtree else 3)
    assert all("--profile" in argv and "TEST" in argv for argv in calls)


def test_governance_default_scope_and_malformed_reads(monkeypatch, capsys):
    path = ROOT / "skills/oci-tenancy-governance/scripts/governance_audit.py"
    spec = importlib.util.spec_from_file_location("governance_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    from lib.oci_ro import prepare

    for key, value in {"PROFILE": "TEST", "REGION": "us-test-1", "TENANCY_ID": "example-tenancy",
                       "COMPARTMENT_ID": "example-tenancy", "OCI_RO_SMOKE_SCOPE": "example-tenancy",
                       "OCI_RO_SMOKE_PROFILE": "TEST", "OCI_RO_SMOKE_REGION": "us-test-1"}.items():
        monkeypatch.setenv(key, value)
    calls = []

    def fake(argv, **kwargs):
        calls.append(prepare(argv, profile=kwargs["profile"], region=kwargs["region"]))
        return {"ok": True, "data": []}

    monkeypatch.setattr(module, "run", fake)
    monkeypatch.setattr(sys, "argv", [str(path)])
    assert module.main() == 0
    report = json.loads(capsys.readouterr().out)
    assert report["include_subtree"] is False and len(calls) == 6
    assert "no_visible_child_compartments_in_sample" in report["findings"]
    monkeypatch.setattr(module, "run", lambda *a, **k: {"ok": True, "data": "malformed"})
    assert module.read([], "TEST", "us-test-1") is None
