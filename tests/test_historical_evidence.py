import copy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/eval'))
import historical_evidence as history


@pytest.mark.parametrize('record', list(json.loads((ROOT / 'evals/historical-evidence.json').read_text())['reports'].values()))
def test_original_verifier_recomputes_archived_scores(record):
    report = json.loads((ROOT / record['path']).read_text())
    result = history.verify_historical(report, record['verifier'])
    assert result['verified'] and result['historical_replay']
    assert result['evidence_revision'] == history.COMMIT
    assert not result['current_sources']
    assert result['model_calls'] == result['cloud_calls'] == 0
    assert result['arms'] == report['arms']


def test_modified_report_cannot_use_historical_replay():
    report = json.loads((ROOT / 'evals/results/checked-task-benchmark-2026-09-11.json').read_text())
    report['results'][0]['passed'] = not report['results'][0]['passed']
    assert history.verify_historical(report, 'verify_checked_task_benchmark.py') is None


def test_verifier_is_not_chosen_by_untrusted_report():
    with pytest.raises(ValueError, match='allowlisted'):
        history.verify_historical({}, 'arbitrary.py')


def test_missing_historical_commit_fails_closed(tmp_path):
    with pytest.raises(ValueError, match='full source Git checkout'):
        history.snapshot(str(tmp_path))


def test_source_currentness_distinguishes_content_changes(tmp_path):
    original = tmp_path / 'original'
    working = tmp_path / 'working'
    for folder in (original, working):
        (folder / 'skills/example').mkdir(parents=True)
        (folder / 'skills/example/SKILL.md').write_text('same')
    assert history.changed_sources({}, working, original) == []
    (working / 'skills/example/SKILL.md').write_text('changed')
    assert history.changed_sources({}, working, original) == ['skills/example/SKILL.md']
