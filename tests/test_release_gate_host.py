"""The default release gate must never silently spend model-provider credits."""
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/ci'))
import release_gate as gate


@pytest.fixture
def scratch(tmp_path):
    output = tmp_path / 'output'
    (output / 'evals/results').mkdir(parents=True)
    return output


def test_default_host_evidence_replays_without_subprocess(monkeypatch, scratch):
    def forbidden(*args, **kwargs):
        pytest.fail('Recorded host evidence must not launch any subprocess')
    monkeypatch.setattr(gate.subprocess, 'run', forbidden)
    monkeypatch.setattr(gate.subprocess, 'check_output', forbidden)
    result = gate.host_evidence(scratch)
    original = json.loads((ROOT / 'evals/results/host.json').read_text())
    assert result['date'] == original['date']
    assert result['status'] == original['status']
    assert result['evidence_mode'] == 'recorded'
    assert result['fresh_model_calls'] == 0
    assert json.loads((scratch / 'evals/results/host.json').read_text()) == result


@pytest.mark.parametrize('contents', [None, '{}', '[]', '{',
                                    '{"status":"pass","date":"2026-09-11","reason":"claims success"}'])
def test_bad_or_missing_host_evidence_does_not_trigger_inference(monkeypatch, scratch, tmp_path, contents):
    source = tmp_path / 'source'
    (source / 'evals/results').mkdir(parents=True)
    if contents is not None:
        (source / 'evals/results/host.json').write_text(contents)
    monkeypatch.setattr(gate, 'ROOT', source)
    def forbidden(*args, **kwargs):
        pytest.fail('Missing or invalid evidence must not trigger inference')
    monkeypatch.setattr(gate, 'probe_host', forbidden)
    result = gate.host_evidence(scratch)
    assert result['status'] == 'unmeasured'
    assert result['fresh_model_calls'] == 0


def test_explicit_probe_dispatch_is_separate(monkeypatch, scratch):
    calls = []
    def fake_probe(output):
        calls.append(output)
        return {'status': 'unmeasured'}
    monkeypatch.setattr(gate, 'probe_host', fake_probe)
    assert gate.host_evidence(scratch, probe=True) == {'status': 'unmeasured'}
    assert calls == [scratch]
