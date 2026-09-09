"""Exercise strict skill consumers through the shared wrapper, without OCI access."""
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from datetime import datetime, timedelta, timezone
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from lib import oci_ro


def skill(path):
    spec = importlib.util.spec_from_file_location('empty_read_consumer', ROOT / 'skills' / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def scope(monkeypatch):
    end = datetime.now(timezone.utc)
    for key, value in {'PROFILE':'DEFAULT', 'REGION':'us-ashburn-1',
                       'COMPARTMENT_ID':'synthetic-root', 'METRIC_NAMESPACE':'oci_computeagent',
                       'MQL':'CpuUtilization[1m].mean()', 'START_TIME':(end-timedelta(hours=1)).isoformat(),
                       'END_TIME':end.isoformat()}.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(sys, 'argv', ['skill'])


@pytest.mark.parametrize('stdout,returncode,expected_exit,kind', [
    ('', 0, 1, 'no_datapoints'), ('[]', 0, 1, 'no_datapoints'),
    ('[{"points":[]}]', 0, 1, 'no_datapoints'),
    ('not json', 0, 2, 'failed_or_malformed_read'),
    ('null', 0, 2, 'failed_or_malformed_read'),
    ('{"wrong":[]}', 0, 2, 'failed_or_malformed_read'),
    ('', 1, 2, 'failed_or_malformed_read'),
    ('[{"points":[{"value":0,"timestamp":"2026-09-09T00:00:00Z"}]}]', 0, 0, None),
])
def test_mql_distinguishes_no_datapoints_from_failed_reads(
        scope, monkeypatch, capsys, stdout, returncode, expected_exit, kind):
    monkeypatch.setattr(oci_ro, 'run_process', lambda *a, **k:
                        SimpleNamespace(returncode=returncode, stdout=stdout, stderr=''))
    module = skill('oci-monitoring-alarms/scripts/validate_mql.py')
    assert module.main() == expected_exit
    result = json.loads(capsys.readouterr().out)
    assert result.get('kind') == kind
    assert result['ok'] == (expected_exit == 0)
    if kind == 'no_datapoints':
        assert result['datapoints'] == 0 and not result['ready_for_review']


@pytest.mark.parametrize('path,count_key', [
    ('oci-vault-certificates/scripts/cert_expiry.py', 'sampled'),
    ('oci-logging-audit/scripts/audit_window.py', 'events'),
])
def test_other_strict_collection_consumers_accept_blank_success(scope, monkeypatch, capsys, path, count_key):
    monkeypatch.setattr(oci_ro, 'run_process', lambda *a, **k:
                        SimpleNamespace(returncode=0, stdout='', stderr=''))
    assert skill(path).main() == 0
    result = json.loads(capsys.readouterr().out)
    assert result['ok'] and result[count_key] == 0
