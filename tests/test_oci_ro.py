"""Exhaustive pure wrapper policy checks; no OCI command is executed."""
import json
import sys
from pathlib import Path

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
