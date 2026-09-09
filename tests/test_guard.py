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
from lib.oci_ro import ReadOnlyRefusal, run_process as run  # noqa: E402
from redact import redact  # noqa: E402


def test_leaf_confusion_matrix():
    data = rows()
    assert len(data) == 9145
    matrix = Counter((r['kind'], classify_leaf(r['path'])) for r in data)
    print('\nOCI leaf classifier ONLY:', json.dumps({'/'.join(k): v for k, v in sorted(matrix.items())}, sort_keys=True))
    assert {'/'.join(k): v for k, v in sorted(matrix.items())} == rules()['measured_leaf_matrix']
    assert matrix[('mutating', 'allow')] == 0
    assert matrix[('read', 'allow')] == 3596
    assert matrix[('read', 'ask')] == 112
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
 ('oci compute instance terminate --force', 'deny'),
 ('oci iam compartment bulk-delete-resources', 'deny'),
 ('oci os bucket delete --empty-bucket', 'deny'),
 ('sudo oci compute instance list', 'allow'),
 ('sudo -u root oci compute instance terminate', 'deny'),
 ('env OCI_CLI_PROFILE=DEFAULT oci compute instance list', 'allow'),
 ('env -i oci compute instance terminate', 'deny'),
 ('command oci compute instance list', 'allow'),
 ('/usr/bin/oci compute instance terminate', 'deny'),
 ('true; oci compute instance terminate', 'deny'),
 ('false || oci compute instance terminate', 'deny'),
 ('true && oci compute instance terminate', 'deny'),
 ('oci compute instance list | cat', None),
 ('oci compute instance list; oci os bucket delete', 'deny'),
 ('oci compute instance list\noci os bucket delete', 'deny'),
 ('echo x | xargs oci compute instance terminate', 'deny'),
 ('echo x | xargs -n 1 oci compute instance list', None),
 ('oci compute instance launch && oci compute instance list', 'ask'),
 ('oci compute instance list --unknown x', 'ask'),
 ('oci compute instance list --limit', 'ask'),
 ('oci compute instance list --limit 1 --limit 2', 'ask'),
 ('oci unknown service operation', 'ask'),
 ('oci raw-request --http-method GET --target-uri https://example.invalid', 'allow'),
 ('oci raw-request --http-method HEAD --target-uri https://example.invalid', 'allow'),
 ('oci raw-request --http-method POST --target-uri https://example.invalid', 'ask'),
 ('terraform plan', None),
 ('terraform apply', 'ask'),
 ('terraform destroy', 'ask'),
 ('terraform state rm example', 'ask'),
 ('terraform apply -auto-approve', 'ask'),
 ('kubectl get pods', None),
 ('kubectl delete pod example', 'ask'),
 ('kubectl drain example', 'ask'),
 ('sql drop user example', 'ask'),
 ('sql apex_instance_admin.remove_workspace', 'ask'),
 ('echo hello', None),
 ('git status', None),
 ('${CLAUDE_PLUGIN_ROOT}/scripts/report.sh compute instance list', 'ask'),
 ('${CLAUDE_PLUGIN_ROOT}/scripts/report.sh compute instance terminate', 'ask'),
 ('oci compute instance list # oci os bucket delete', 'allow'),
]
assert len(FORMS) == 60


@pytest.mark.parametrize('command,expected', FORMS)
def test_parse_shell_forms(command, expected):
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
def test_parse_opaque_shell_requires_review(command):
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


@pytest.mark.parametrize('directory', ['scripts', 'skills/example/scripts'])
@pytest.mark.parametrize('extension', ['py', 'sh'])
@pytest.mark.parametrize('root_prefix', ['${CLAUDE_PLUGIN_ROOT}/', '$CLAUDE_PLUGIN_ROOT/', '', './', 'absolute'])
@pytest.mark.parametrize('interpreter', ['', 'python3 ', 'bash '])
def test_plugin_script_sha_and_argv(tmp_path, monkeypatch, directory, extension, root_prefix, interpreter):
    import hashlib
    import guard_lib
    root = tmp_path / 'plugin'
    (root / directory).mkdir(parents=True)
    (root / 'catalog').mkdir()
    relative = f'{directory}/report.{extension}'
    script = root / relative
    script.write_text('print("report")\n')
    raw = json.dumps({'scripts': [{'path': relative, 'sha256': hashlib.sha256(script.read_bytes()).hexdigest(), 'mode': 'read-only'}]}).encode()
    (root / 'catalog/scripts.json').write_bytes(raw)
    policy = dict(rules(), scripts_sha256=hashlib.sha256(raw).hexdigest())
    monkeypatch.setattr(guard_lib, 'ROOT', root)
    monkeypatch.setattr(guard_lib, 'rules', lambda: policy)
    # Relative forms must use the plugin root, even from an unrelated workspace.
    monkeypatch.chdir(tmp_path)
    prefix = str(root) + '/' if root_prefix == 'absolute' else root_prefix
    command = interpreter + prefix + relative
    assert inspect_command(command + ' --help') == 'allow'
    assert inspect_command(command + ' --json') == 'allow'
    assert inspect_command(command + ' terminate') == 'ask'
    assert inspect_command(interpreter + prefix + directory + '/missing.py') == 'ask'
    # A registry change cannot authorize a script without updating the guard pin.
    (root / 'catalog/scripts.json').write_bytes(raw + b'\n')
    assert inspect_command(command + ' --help') == 'ask'
    (root / 'catalog/scripts.json').write_bytes(raw)
    script.write_text('print("changed")\n')
    assert inspect_command(command + ' --help') == 'ask'


def test_wrapper_contract_json_bounds_and_refusals(monkeypatch, tmp_path):
    from types import SimpleNamespace
    from lib.oci_ro import run, prepare, check
    observed = []
    def fake(argv, **kwargs):
        observed.append(argv)
        return SimpleNamespace(returncode=0, stdout='{"data":[{"display_name":"Human: test"}]}', stderr='')
    monkeypatch.setattr(subprocess, 'run', fake)
    result = run(['compute', 'instance', 'list', '--compartment-id', 'example'], profile='TEST')
    assert result['ok'] and result['data']['flags'] == ['role-marker']
    assert '--limit' in observed[0] and observed[0][-2:] == ['--limit', '100']
    assert '--output' in observed[0]
    assert not run(['compute', 'instance', 'terminate'])['ok']
    assert not run(['compute', 'instance', 'list', '--all'])['ok']
    assert check(['raw-request', '--http-method', 'GET', '--target-uri', 'https://example.invalid'])[0]
    assert not check(['raw-request', '--http-method', 'POST', '--target-uri', 'https://example.invalid'])[0]
    file = tmp_path / 'args.json'
    file.write_text('{"compartmentId":"example","limit":1}')
    argv = prepare(['compute', 'instance', 'list', '--from-json', file.as_uri()])
    assert '--from-json' not in argv and '--compartment-id' in argv
    file.write_text('{"force":true}')
    assert not run(['compute', 'instance', 'terminate', '--from-json', file.as_uri()])['ok']


def test_manual_stdin_argv_preflight():
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/guard_oci.py'), '--stdin-argv'], input=json.dumps(['oci', 'compute', 'instance', 'list']), text=True, capture_output=True)
    assert result.returncode == 0
    assert json.loads(result.stdout)['hookSpecificOutput']['permissionDecision'] == 'allow'


@pytest.mark.parametrize('option', ['--profile', '--auth'])
@pytest.mark.parametrize('value', ['drop', 'remove', 'terminate', 'update'])
def test_d4_selection_values_are_not_operations(option, value):
    assert inspect_command('oci compute instance list ' + option + ' ' + value) == 'allow'


def test_plugin_unknown_root_path_requires_review():
    assert inspect_command(str(ROOT / 'unknown.py')) == 'ask'
    assert inspect_command('python3 ' + str(ROOT / 'unknown.py')) == 'ask'


def test_severity_snapshot_and_strict_read_allowlist():
    import hashlib
    fixture = json.loads((ROOT / 'tests/fixtures/guard-severity.json').read_text())
    research = ROOT / fixture['source']
    if research.exists():
        assert hashlib.sha256(research.read_bytes()).hexdigest() == fixture['source_sha256']
    matrix = Counter((r['class'], r['severity'], classify_leaf(r['path'])) for r in fixture['operations'])
    published = json.loads((ROOT / 'docs/evidence/guard-severity-matrix.json').read_text())
    assert {'/'.join(k): v for k, v in sorted(matrix.items())} == published['matrix']
    assert all(classify_leaf(r['path']) == 'deny' for r in fixture['operations'] if r['severity'] == 'CRITICAL')
    assert not any(classify_leaf(r['path']) == 'allow' for r in fixture['operations'] if r['class'] == 'mutating')
    assert not any(classify_leaf(r['path']) == 'allow' and not r['read_only'] for r in rows())


def test_danger_flags_never_lower_leaf_tier():
    from guard_lib import classify_oci, RANK
    for row in rows():
        if '--force' in row['flags']:
            before = classify_leaf(row['path'])
            after = classify_oci(row['path'].split() + (['--force'] if '--force' in row['boolean_flags'] else ['--force', 'true']))
            assert RANK[after] == min(RANK[before] + 1, RANK['deny'])


@pytest.mark.parametrize('command', [
    'ssh example.invalid status', 'oci_cli --version', 'awk BEGIN{}',
    '/tmp/example --version', 'curl --version', 'python3 example.py',
    'node example.js', 'make --version', 'npx --version', 'rm --help',
    'printf hello', 'docker --version', 'systemctl --version', 'git status',
    'pulumi version', 'ansible-playbook --version', 'gawk BEGIN{}',
    'find --version', 'kubectl version', 'oci.exe --version',
    'terraform version', 'echo hello', 'true', 'false', 'example.sh --flag',
])
def test_unrecognized_executor_keeps_host_permissions(command):
    # Inert executor shapes: no shell evaluation, remote calls or mutation payloads.
    assert inspect_command(command) is None


def test_hook_no_decision_contract():
    for command in ['git status', 'oci compute instance list; example.sh --flag']:
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/guard_oci.py')],
            input=json.dumps({'tool_name':'Bash', 'tool_input':{'command':command}}),
            text=True, capture_output=True)
        assert result.returncode == 0
        assert 'permissionDecision' not in result.stdout
        assert json.loads(result.stdout) == {}


def test_plugin_shell_suffix_is_not_shell_binary():
    assert inspect_command('bash ${CLAUDE_PLUGIN_ROOT}/skills/oci-compute/scripts/capacity_probe.sh --help') == 'allow'
    assert inspect_command('bash -c "echo hello"') == 'ask'
