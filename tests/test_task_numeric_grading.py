"""JSON value equality in task grading, independent of decimal spelling."""
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/eval'))
from tool_task_benchmark import grade, same_json_value


@pytest.mark.parametrize('actual,expected', [
    (20.0, 20), (30, 30.0), (-0.0, 0), (1e30, 10 ** 30),
    ({'samples': [20.0, {'maximum': 30.0}]}, {'samples': [20, {'maximum': 30}]}),
])
def test_equivalent_json_numbers(actual, expected):
    assert same_json_value(actual, expected)
    assert same_json_value(expected, actual)


@pytest.mark.parametrize('actual,expected', [
    (True, 1), (False, 0.0), ('20', 20), (20.01, 20),
    (0.1 + 0.2, 0.3), (float('nan'), float('nan')),
    (float('inf'), float('inf')), (float('-inf'), float('-inf')),
    ([1, 2], [2, 1]), ([1], [1, 1]),
    ({'a': 20, 'extra': False}, {'a': 20}),
    ({'answer': True}, {'answer': 1}), (None, False),
])
def test_wrong_types_values_order_and_nonfinite_values_still_fail(actual, expected):
    assert not same_json_value(actual, expected)
    assert not same_json_value(expected, actual)


def test_numeric_equivalence_does_not_remove_evidence_requirement():
    fixture = {'topic': 'cpu_metrics', 'expected': {'mean': 20, 'maximum': 30}}
    answer = {'mean': 20.0, 'maximum': 30.0}
    assert grade(fixture, answer, []) == {
        'answer_correct': True, 'required_evidence_read': False, 'passed': False}
    assert not grade(fixture, answer, [{'topic': 'cpu_metrics', 'ok': False}])['passed']
    assert grade(fixture, answer, [{'topic': 'cpu_metrics', 'ok': True}])['passed']
