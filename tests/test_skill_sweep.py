"""Sweep classifications must preserve failures separately from missing data."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from datetime import datetime, timedelta
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from check_skill_scripts import outcome
import check_skill_scripts as sweep


def test_explicit_empty_evidence_is_a_gap():
    assert outcome(1, json.dumps({'ok': False, 'kind': 'no_datapoints'}), '') == 'ran, gap'
    assert outcome(0, json.dumps({'ok': True, 'data': []}), '') == 'passed'


def test_service_and_malformed_errors_are_not_gaps():
    for value in ({'ok': False, 'kind': 'failed_or_malformed_read'},
                  {'ok': False, 'error': {'kind': 'service', 'status': 404}},
                  {'ok': False, 'steps': [{'ok': False, 'kind': 'no_datapoints'},
                                         {'ok': False, 'error': {'kind': 'refused'}}]}):
        assert outcome(1, json.dumps(value), '') == 'failed'
    assert outcome(2, '{"ok":false,"kind":"no_datapoints"}', '') == 'failed'
    assert outcome(1, '{"ok":false,"kind":"no_datapoints"} broken', '') == 'failed'


def test_missing_prerequisite_remains_blocked():
    assert outcome(2, '', 'Set PROJECT_ID') == 'blocked_missing_prerequisite'


@pytest.mark.parametrize('instance_response,instance_code,expected', [
    ('"synthetic-instance"', 0, 'passed'),
    ('', 0, 'skipped: no instance'),
    ('', 1, 'blocked_missing_prerequisite'),
])
def test_sweep_derives_scope_and_skips_only_confirmed_absence(
        tmp_path, monkeypatch, instance_response, instance_code, expected):
    from lib import oci_ro
    config = tmp_path / 'config'
    config.write_text('[DEFAULT]\ntenancy=synthetic-root\nregion=us-ashburn-1\n')
    monkeypatch.setenv('OCI_CLI_CONFIG_FILE', str(config))
    monkeypatch.setenv('INSTANCE_ID', 'inherited-wrong-instance')
    monkeypatch.setenv('MQL', 'inherited-wrong-query')
    monkeypatch.setenv('REGION', 'inherited-wrong-region')
    directory = tmp_path / 'skills/example/scripts'
    directory.mkdir(parents=True)
    for name in ('triage.py', 'triage.sh', 'validate_mql.py'):
        (directory / name).touch()
    monkeypatch.setattr(sweep, 'ROOT', tmp_path)
    report_path = tmp_path / 'report.json'
    monkeypatch.setattr(sys, 'argv', ['sweep', '--live', '--report', str(report_path)])

    def discover(argv, **kwargs):
        assert argv[argv.index('--compartment-id') + 1] == 'synthetic-root'
        assert argv[argv.index('--profile') + 1] == 'DEFAULT'
        assert argv[argv.index('--region') + 1] == 'us-ashburn-1'
        assert '--no-retry' in argv
        if argv[:3] == ['compute', 'instance', 'list']:
            assert argv[argv.index('--limit') + 1] == '1'
            return SimpleNamespace(returncode=instance_code, stdout=instance_response)
        return SimpleNamespace(returncode=0, stdout='"synthetic-prerequisite"')

    executed = []
    def execute(command, *, env, **kwargs):
        executed.append(Path(command[1]).name)
        assert env['PROFILE'] == 'DEFAULT' and env['REGION'] == 'us-ashburn-1'
        assert env['TENANCY_ID'] == env['COMPARTMENT_ID'] == env['OCI_RO_SMOKE_SCOPE'] == 'synthetic-root'
        assert env['METRIC_NAMESPACE'] == 'oci_computeagent'
        assert env['MQL'] == 'CpuUtilization[1m].mean()'
        assert datetime.fromisoformat(env['END_TIME']) - datetime.fromisoformat(env['START_TIME']) == timedelta(hours=1)
        if Path(command[1]).name.startswith('triage') and not env.get('INSTANCE_ID'):
            return SimpleNamespace(returncode=2, stdout='', stderr='Set INSTANCE_ID')
        if env.get('INSTANCE_ID'):
            assert env['INSTANCE_ID'] == 'synthetic-instance'
        return SimpleNamespace(returncode=0, stdout='{"ok":true}', stderr='')

    monkeypatch.setattr(oci_ro, 'run_process', discover)
    monkeypatch.setattr(sweep.subprocess, 'run', execute)
    sweep.main()
    report = json.loads(report_path.read_text())
    assert {r['status'] for r in report['checks'] if 'triage' in r['script']} == {expected}
    assert ('triage.py' in executed) == (expected != 'skipped: no instance')
    assert 'synthetic-root' not in report_path.read_text()
