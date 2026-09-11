import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pilot', ROOT/'scripts/eval/task_answer_pilot.py')
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)
sys.path.insert(0, str(ROOT/'scripts/eval'))
from verify_task_answer_pilot import verify


def test_expected_answers_are_not_in_model_payload():
    config = json.loads(pilot.FIXTURES.read_text())
    for case in config['cases']:
        for arm in ('with-reference', 'without-reference'):
            result = pilot.payload(case, arm)
            assert 'expected' not in result and 'id' not in result and 'skill' not in result
            assert result['observations'] == case['evidence']
            assert ('reference' in result) == (arm == 'with-reference')


def test_missing_attempts_are_not_a_complete_pilot():
    rows = [{'arm': 'with-reference', 'completed': True, 'passed': True}]
    result = pilot.summarize(rows, 24)
    assert result['complete'] is False
    assert result['arms']['without-reference'] == {'passed': 0, 'attempts': 0}


def test_model_tools_invalidate_answer_evidence():
    import pytest
    init = {'type': 'system', 'subtype': 'init', 'tools': ['Bash']}
    result = {'type': 'result', 'subtype': 'success', 'result': '{}'}
    with pytest.raises(ValueError):
        pilot.parse_transcript('\n'.join(map(json.dumps, [init, result])))


def test_recorded_pilot_scores_are_recomputed():
    report = json.loads((ROOT/'evals/results/task-answer-pilot-2026-09-11.json').read_text())
    assert verify(report)['verified'] is True


def test_duplicate_or_changed_pilot_answers_fail():
    import pytest
    path = ROOT/'evals/results/task-answer-pilot-2026-09-11.json'
    report = json.loads(path.read_text())
    report['results'][0]['trace']['answer'] = {'invented': True}
    with pytest.raises(ValueError, match='Answer score'):
        verify(report)
    report = json.loads(path.read_text())
    report['results'][0] = report['results'][1]
    with pytest.raises(ValueError, match='Missing or repeated'):
        verify(report)
