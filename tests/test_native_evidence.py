import copy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/eval'))
import verify_native_task_benchmark as verifier


@pytest.fixture
def report():
    return json.loads((ROOT / 'evals/results/native-task-benchmark-2026-09-11.json').read_text())


def test_recorded_native_evidence_is_consistent(report):
    assert verifier.verify(report)['verified']


@pytest.mark.parametrize('mutation', ['pair', 'hash', 'cost', 'activation', 'receipt', 'score'])
def test_native_evidence_rejects_tampering(report, mutation):
    report = copy.deepcopy(report)
    row = next(r for r in report['results'] if r['completed'] and r['receipts'])
    if mutation == 'pair':
        report['results'].append(report['results'][0])
    elif mutation == 'hash':
        report['source_sha256'].pop(next(iter(report['source_sha256'])))
    elif mutation == 'cost':
        report['reported_cost_usd'] += 1
    elif mutation == 'activation':
        row['native_skill_activated'] = not row['native_skill_activated']
    elif mutation == 'receipt':
        row['receipts'] = []
    else:
        row['passed'] = not row['passed']
    with pytest.raises(ValueError):
        verifier.verify(report)
