import copy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/eval'))
import task_repair_regression as regression
from verify_checked_task_benchmark import verify as verify_full


@pytest.fixture
def report():
    return json.loads((ROOT / 'evals/results/task-repair-regression-2026-09-11.json').read_text())


def test_recorded_regression_has_current_sources_and_explicit_limited_scope(report):
    result = regression.verify(report)
    assert result['verified'] and result['current_sources']
    assert not result['full_task_certification']
    assert set(result['case_ids']) == set(regression.CASES)


def test_five_case_regression_cannot_pass_the_full_verifier(report):
    with pytest.raises(ValueError, match='Missing/duplicate'):
        verify_full(report)


@pytest.mark.parametrize('field', ['scope', 'source', 'score', 'cost', 'pair'])
def test_regression_evidence_rejects_changes(report, field):
    report = copy.deepcopy(report)
    if field == 'scope':
        report['full_task_certification'] = True
    elif field == 'source':
        report['regression_collector_sha256'] = '0' * 64
    elif field == 'score':
        report['results'][0]['passed'] = not report['results'][0]['passed']
    elif field == 'cost':
        report['reported_cost_usd'] += 1
    else:
        report['results'].append(report['results'][0])
    with pytest.raises(ValueError):
        regression.verify(report)
