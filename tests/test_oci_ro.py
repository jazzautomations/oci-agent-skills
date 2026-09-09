"""Exhaustive pure wrapper policy checks; no OCI command is executed."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from lib.oci_ro import check, run  # noqa: E402
from lib.redact import redact  # noqa: E402


def test_wrapper_replays_all_catalog_leaves():
    rows = [json.loads(line) for line in (ROOT / 'catalog/cli.jsonl').read_text().splitlines()]
    assert len(rows) == 9145
    for row in rows:
        assert check(row['path'].split())[0] == row['read_only'], row['path']
    assert not check(['ce', 'cluster', 'create-kubeconfig'])[0]
    assert sum(row['read_only'] for row in rows) == 3601


def test_wrapper_service_errors_never_echo_raw_output(monkeypatch):
    from types import SimpleNamespace
    import lib.oci_ro as wrapper
    monkeypatch.setattr(wrapper, 'run_process', lambda *a, **k: SimpleNamespace(returncode=1, stderr='ServiceError: {"status":403,"message":"private data"}', stdout=''))
    result = run(['os', 'ns', 'get'])
    assert result['error'] == {'kind': 'service', 'status': 403}
    assert 'private data' not in json.dumps(result)
    assert 'sensitive' not in redact('Bearer sensitive')


@pytest.mark.parametrize('path', [
    'compute instance list', 'monitoring metric-data summarize-metrics-data',
    'certs-mgmt certificate list', 'monitoring alarm-status list-alarms-status',
    'usage-api usage-summary request-summarized-usages',
])
@pytest.mark.parametrize('sanitize', [False, True])
def test_blank_collection_response_is_successful_empty_list(monkeypatch, path, sanitize):
    import lib.oci_ro as wrapper
    monkeypatch.setattr(wrapper, 'run_process', lambda *a, **k:
                        SimpleNamespace(returncode=0, stdout=' \n', stderr=''))
    result = run(path.split(), sanitize=sanitize)
    assert result['ok']
    assert (result['data']['items'] if sanitize else result['data']) == []
    assert not result['truncated']


@pytest.mark.parametrize('stdout,expected', [('', None), ('null', None), ('not json', 'not json')])
def test_get_and_nonempty_malformed_responses_are_not_empty_lists(monkeypatch, stdout, expected):
    import lib.oci_ro as wrapper
    monkeypatch.setattr(wrapper, 'run_process', lambda *a, **k:
                        SimpleNamespace(returncode=0, stdout=stdout, stderr=''))
    assert run(['os', 'ns', 'get'], sanitize=False)['data'] == expected
    if stdout:
        assert run(['compute', 'instance', 'list'], sanitize=False)['data'] == expected


def test_failed_collection_read_never_becomes_an_empty_success(monkeypatch):
    import lib.oci_ro as wrapper
    monkeypatch.setattr(wrapper, 'run_process', lambda *a, **k:
                        SimpleNamespace(returncode=1, stdout='', stderr='ServiceError: {"status":403}'))
    result = run(['compute', 'instance', 'list'], sanitize=False)
    assert not result['ok'] and result['error']['status'] == 403
    assert 'data' not in result
