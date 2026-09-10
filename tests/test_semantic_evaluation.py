"""Selection evidence must be blind, complete, current and scored from predictions."""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('semantic_eval', ROOT / 'scripts/eval/semantic.py')
semantic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(semantic)


def test_model_payload_excludes_answers_and_case_categories():
    candidates = [{'name': 'network', 'description': 'Network troubleshooting', 'private_note': 'hidden'}]
    rows = [{'id': 'R01', 'prompt': 'Network timeout', 'expected_skill': 'secret-answer'},
            {'id': 'N01', 'prompt': 'Bake a cake', 'trap': 'secret-trap'}]
    payload, mapping = semantic.blind_payload(candidates, rows, 17)
    rendered = json.dumps(payload)
    for forbidden in ['R01', 'N01', 'expected_skill', 'trap', 'secret', 'private_note', 'hidden']:
        assert forbidden not in rendered
    assert set(mapping.values()) == {'R01', 'N01'}
    assert {r['prompt'] for r in payload['requests']} == {'Network timeout', 'Bake a cake'}
    changed = copy.deepcopy(rows)
    changed[0]['expected_skill'] = 'another-label'
    assert semantic.blind_payload(candidates, changed, 17) == (payload, mapping)


@pytest.mark.parametrize('labels', [
    [], [{'id': 'item000', 'skill': 'invented'}],
    [{'id': 'item000', 'skill': 'network'}, {'id': 'item000', 'skill': None}],
    [{'id': 'R01', 'skill': 'network'}], [{'id': 'item000', 'skill': 'null'}],
])
def test_incomplete_duplicate_unknown_predictions_fail(labels):
    with pytest.raises(ValueError):
        semantic.parse_labels({'labels': labels}, {'item000': 'R01'}, [{'name': 'network'}])


def test_scope_abstention_is_a_real_json_null():
    assert semantic.parse_labels({'labels': [{'id': 'item000', 'skill': None}]},
                                 {'item000': 'N01'}, [{'name': 'network'}]) == {'N01': None}


def transcript(*, tools=None, message=None):
    events = [{'type': 'system', 'subtype': 'init', 'model': 'fixture-model',
               'tools': tools or [], 'mcp_servers': []}]
    if message:
        events.append({'type': 'assistant', 'message': {'content': [message]}})
    events.append({'type': 'result', 'subtype': 'success', 'is_error': False,
                   'session_id': 'fixture-session', 'result': '{"labels":[]}'})
    return '\n'.join(json.dumps(e) for e in events)


def test_tool_access_or_calls_invalidate_classifier_trial():
    with pytest.raises(ValueError):
        semantic.parse_transcript(transcript(tools=['Bash']))
    with pytest.raises(ValueError):
        semantic.parse_transcript(transcript(message={'type': 'tool_use', 'name': 'Read'}))
    labels, trace = semantic.parse_transcript(transcript())
    assert labels == {'labels': []}
    assert trace['model'] == 'fixture-model'


def fake_evidence(tmp_path, monkeypatch):
    candidates, files, fingerprint = semantic.inputs()
    remap = files['remap.json']
    oracle = {r['id']: remap.get(r['expected_skill'], r['expected_skill']) for r in files['routing.json']}
    oracle.update({r['id']: None for r in files['negatives.json']})
    records = []
    for seed in files['semantic-policy.json']['seeds']:
        payload, mapping = semantic.blind_payload(candidates, files['routing.json'] + files['negatives.json'], seed)
        records.append({'seed': seed, 'input_sha256': semantic.digest(payload),
                        'trace': {'model': files['semantic-policy.json']['model'], 'session_id': f'fixture-{seed}',
                                  'tools': [], 'mcp_servers': [],
                                  'result': {'labels': [{'id': k, 'skill': oracle[v]} for k, v in mapping.items()]}},
                        'score': semantic.score(oracle, files)})
    data = {'version': 1, 'complete': True, 'mode': files['semantic-policy.json']['method'],
            'inputs_sha256': fingerprint, 'cli_version': 'test fixture', 'validated_at': '2026-09-10',
            'runs': records, 'ok': True}
    path = tmp_path / 'synthetic-evidence.json'
    path.write_text(json.dumps(data))
    return path, data


@pytest.mark.parametrize('tamper', ['stale', 'score', 'duplicate_session', 'missing_trial', 'partial'])
def test_replay_rejects_invalid_provenance_or_scores(tmp_path, monkeypatch, tamper):
    path, data = fake_evidence(tmp_path, monkeypatch)
    assert semantic.verify(report=path)['ok']
    if tamper == 'stale':
        data['inputs_sha256'] = 'stale'
    elif tamper == 'score':
        data['runs'][0]['score']['metrics']['correct'] = 0
    elif tamper == 'duplicate_session':
        data['runs'][1]['trace']['session_id'] = data['runs'][0]['trace']['session_id']
    elif tamper == 'missing_trial':
        data['runs'].pop()
    else:
        data['complete'] = False
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        semantic.verify(report=path)


def test_one_negative_firing_fails_even_with_perfect_positive_accuracy(tmp_path, monkeypatch):
    candidates, files, _ = semantic.inputs()
    remap = files['remap.json']
    selections = {r['id']: remap.get(r['expected_skill'], r['expected_skill']) for r in files['routing.json']}
    selections.update({r['id']: None for r in files['negatives.json']})
    selections[files['negatives.json'][0]['id']] = candidates[0]['name']
    result = semantic.score(selections, files)
    assert result['metrics']['accuracy'] == 1
    assert not result['gates']['V20'] and not result['ok']


def test_boundary_counterexample_preserves_enrolled_external_database():
    cases = json.loads((ROOT / 'evals/semantic-boundaries.json').read_text())['cases']
    assert next(r for r in cases if r['id'] == 'B01')['expected_skill'] == 'oracle-db-fleet'
    assert next(r for r in cases if r['id'] == 'B08')['expected_skill'] is None


def test_missing_semantic_evidence_cannot_fall_back_to_lexical_pass(monkeypatch):
    import sys
    sys.path.insert(0, str(ROOT / 'scripts/eval'))
    run_spec = importlib.util.spec_from_file_location('evaluation_run', ROOT / 'scripts/eval/run.py')
    runner = importlib.util.module_from_spec(run_spec)
    run_spec.loader.exec_module(runner)
    base = {'routing': [], 'negatives': [], 'tasks': [], 'metrics': {
        'routing_accuracy': 1, 'routing_count': 80, 'overlap_pairs_correct': 4,
        'negative_firings': 0, 'negative_count': 40},
        'gates': {'V19': True, 'V20': True, 'command_validity': False}}
    monkeypatch.setattr(runner, 'run_legacy', lambda: copy.deepcopy(base))
    def missing(*args, **kwargs):
        raise ValueError('No current evidence')
    monkeypatch.setattr(runner.semantic, 'verify', missing)
    monkeypatch.setattr(runner.boundaries, 'verify', missing)
    result = runner.run()
    assert not result['ok']
    assert result['metrics']['routing_accuracy'] is None
    assert not any(result['gates'].values())
    assert result['legacy']['metrics']['routing_accuracy'] == 1
