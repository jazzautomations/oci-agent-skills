"""Offline guard tests: catalog replay and shell fixtures never execute OCI or payloads."""
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from catalog import rows  # noqa: E402
from guard_lib import classify_leaf, inspect_command, readonly_argv, rules  # noqa: E402
from lib.oci_ro import ReadOnlyRefusal, run  # noqa: E402
from redact import redact  # noqa: E402


def test_leaf_confusion_matrix():
    data = rows()
    assert len(data) == 9145
    matrix = Counter((r['kind'], classify_leaf(r['path'])) for r in data)
    print('\nOCI leaf classifier ONLY:', json.dumps({'/'.join(k): v for k, v in sorted(matrix.items())}, sort_keys=True))
    assert {'/'.join(k): v for k, v in sorted(matrix.items())} == rules()['measured_leaf_matrix']
    assert matrix[('mutating', 'allow')] == 0
    assert matrix[('read', 'allow')] == 3697
    assert matrix[('read', 'ask')] == 11
    assert matrix[('destructive', 'allow')] == 1  # estimate-release-data-size is a census false positive.
    assert all(classify_leaf(r['path']) == 'deny' for r in data if r['severity'] == 'CRITICAL')


# 60 explicit shell forms, including mixed commands and option/value ambiguity.
FORMS = [
 ('oci compute instance list', 'allow'),
 ('oci compute instance terminate', 'deny'),
 ('oci compute instance launch', 'ask'),
 ('oci os bucket delete', 'deny'),
 ('oci iam user delete', 'ask'),
 ('oci --profile alternate compute instance list', 'allow'),
 ('oci --auth instance_principal compute instance list', 'allow'),
 ('oci compute instance list --profile alternate', 'allow'),
 ('oci compute instance list --auth security_token', 'allow'),
 ('oci compute instance list --display-name "terminate"', 'allow'),
 ('oci compute instance list --display-name "a; b"', 'allow'),
 ('oci compute instance list --display-name "a && b"', 'allow'),
 ('oci compute instance list --display-name "a | b"', 'allow'),
 ('oci compute instance list --display-name "delete"', 'allow'),
 ('oci compute instance list --limit=1', 'allow'),
 ('oci compute instance list --all', 'allow'),
 ('oci compute instance terminate --help', 'allow'),
 ('oci compute instance --help', 'allow'),
 ('oci --help', 'allow'),
 ('oci compute instance list --from-json file://input.json', 'ask'),
 ('oci compute instance terminate --force', 'ask'),
 ('oci iam compartment bulk-delete-resources', 'ask'),
 ('oci os bucket delete --empty-bucket', 'ask'),
 ('sudo oci compute instance list', 'allow'),
 ('sudo -u root oci compute instance terminate', 'deny'),
 ('env OCI_CLI_PROFILE=DEFAULT oci compute instance list', 'allow'),
 ('env -i oci compute instance terminate', 'deny'),
 ('command oci compute instance list', 'allow'),
 ('/usr/bin/oci compute instance terminate', 'deny'),
 ('true; oci compute instance terminate', 'deny'),
 ('false || oci compute instance terminate', 'deny'),
 ('true && oci compute instance terminate', 'deny'),
 ('oci compute instance list | cat', 'allow'),
 ('oci compute instance list; oci os bucket delete', 'deny'),
 ('oci compute instance list\noci os bucket delete', 'deny'),
 ('echo x | xargs oci compute instance terminate', 'deny'),
 ('echo x | xargs -n 1 oci compute instance list', 'allow'),
 ('oci compute instance launch && oci compute instance list', 'ask'),
 ('oci compute instance list --unknown x', 'ask'),
 ('oci compute instance list --limit', 'ask'),
 ('oci compute instance list --limit 1 --limit 2', 'ask'),
 ('oci unknown service operation', 'ask'),
 ('oci raw-request --http-method GET --target-uri https://example.invalid', 'allow'),
 ('oci raw-request --http-method HEAD --target-uri https://example.invalid', 'allow'),
 ('oci raw-request --http-method POST --target-uri https://example.invalid', 'ask'),
 ('terraform plan', 'allow'),
 ('terraform apply', 'ask'),
 ('terraform destroy', 'ask'),
 ('terraform state rm example', 'ask'),
 ('terraform apply -auto-approve', 'ask'),
 ('kubectl get pods', 'allow'),
 ('kubectl delete pod example', 'ask'),
 ('kubectl drain example', 'ask'),
 ('sql drop user example', 'ask'),
 ('sql apex_instance_admin.remove_workspace', 'ask'),
 ('echo hello', 'allow'),
 ('git status', 'allow'),
 ('${CLAUDE_PLUGIN_ROOT}/scripts/report.sh compute instance list', 'allow'),
 ('${CLAUDE_PLUGIN_ROOT}/scripts/report.sh compute instance terminate', 'deny'),
 ('oci compute instance list # oci os bucket delete', 'allow'),
]
assert len(FORMS) == 60


@pytest.mark.parametrize('command,expected', FORMS)
def test_shell_forms(command, expected):
    assert inspect_command(command) == expected


BYPASSES = [
 'eval "oci compute instance list"', 'bash -c "oci compute instance list"',
 'sh -c "$CMD"', 'echo placeholder | base64 -d | sh',
 'printf placeholder | sh', 'python -c "import oci"', 'python3 -c "import oci"',
 'node -e "process.exit()"', 'perl -e "exit"', 'ruby -e "exit"',
 'oci compute instance $VERB', 'oci compute instance ${VERB}',
 '$OCI compute instance list', '`echo oci` compute instance list',
 '$(echo oci) compute instance list', 'echo $(oci compute instance list)',
 'source script.sh', '. script.sh', 'xxd -r payload | bash',
 'oci compute instance list --from-json file://opaque.json',
]
assert len(BYPASSES) == 20


@pytest.mark.parametrize('command', BYPASSES)
def test_opaque_shell_requires_review(command):
    assert inspect_command(command) != 'allow'


def test_hook_contract_and_redaction():
    for command, expected, code in [('oci os bucket delete', 'deny', 2), ('oci compute instance list', 'allow', 0)]:
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/guard_oci.py')],
            input=json.dumps({'tool_name': 'Bash', 'tool_input': {'command': command}}), text=True, capture_output=True)
        assert result.returncode == code
        assert json.loads(result.stdout)['hookSpecificOutput']['permissionDecision'] == expected
    assert 'sensitive' not in redact('Bearer sensitive password=sensitive authToken:sensitive /p/sensitive/n/')
    assert 'abcdefgh' not in redact('ocid1.tenancy.oc1..abcdefgh')


def test_wrapper_refuses_without_subprocess(monkeypatch):
    monkeypatch.setattr(subprocess, 'run', lambda *a, **k: pytest.fail('must not execute'))
    for argv in [['compute', 'instance', 'terminate'], ['raw-request', '--http-method', 'GET'], ['compute', 'instance', 'list', '--from-json', 'file://input']]:
        with pytest.raises(ReadOnlyRefusal):
            run(argv)
    assert readonly_argv(['compute', 'instance', 'terminate', '--generate-full-command-json-input'])
    assert readonly_argv(['os', 'ns', 'get'])


def test_hook_import_failure_is_review_without_payload_echo(tmp_path):
    import shutil
    shutil.copy(ROOT / 'scripts/guard_oci.py', tmp_path / 'guard_oci.py')
    result = subprocess.run([sys.executable, '-I', str(tmp_path / 'guard_oci.py')],
        input=json.dumps({'tool_name': 'Bash', 'tool_input': {'command': 'secret-input'}}),
        text=True, capture_output=True)
    assert result.returncode == 0
    assert json.loads(result.stdout)['hookSpecificOutput']['permissionDecision'] == 'ask'
    assert 'secret-input' not in result.stdout


@pytest.mark.parametrize('option', ['--profile', '--auth', '--compartment-id'])
def test_variable_option_values_do_not_change_leaf(option):
    assert inspect_command('oci compute instance list ' + option + ' "$VALUE"') == 'allow'


def test_opaque_segment_does_not_downgrade_a_known_denial():
    assert inspect_command('oci os bucket delete; eval "$CMD"') == 'deny'
