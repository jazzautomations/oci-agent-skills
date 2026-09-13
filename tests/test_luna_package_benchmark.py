import copy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/eval'))
import verify_luna_package_benchmark as verifier


@pytest.fixture
def report():
    benchmark = verifier.benchmark
    task = next(t for t in json.loads((ROOT / 'evals/tasks.json').read_text()) if t['id'] == 'T39')
    fixture = next(f for f in json.loads((ROOT / 'evals/tool-task-fixtures.json').read_text())['cases'] if f['id'] == 'T39')
    rows = []
    for arm in verifier.ARMS:
        answer = {'answer': {'executed': False, 'needs_review': True}, 'commands': []}
        rows.append({'arm': arm, 'case': 'T39',
                     'input_sha256': benchmark.previous.original.digest(benchmark.previous.original.payload(task, fixture)),
                     'answer': answer, 'schema_valid': True, 'completed': True, 'passed': True,
                     'grades': {'answer_correct': True, 'required_evidence_read': True, 'passed': True,
                                'commands_valid': True, 'contract_valid': True, 'each_final_command_checked': True},
                     'receipts': [], 'calls': [], 'loaded_skills': [], 'reference_reads': [], 'action_count': 0,
                     'events': [{'case': 'T39', 'action': 'submit', 'success': True,
                                 'request': {'case': 'T39', 'action': 'submit', 'answer': answer}}]})
    return {'format_version': 1, 'model': 'gpt-5.6-luna', 'source_sha256': benchmark.fingerprints(),
            'protocol': {'tasks': ['T39'], 'arms': list(verifier.ARMS), 'order_seed': 915,
                         'runs_per_task_arm': 1, 'max_actions_per_case': 16,
                         'max_observations_per_case': 8, 'max_wall_seconds': 2700},
            'packages': {arm: {'skills': []} for arm in verifier.ARMS}, 'results': rows, 'collected_all': True,
            'arms': {arm: {'submitted': 1, 'completed': 1, 'passed': 1,
                           'cases_with_skill_read': 0, 'cases_with_reference_read': 0} for arm in verifier.ARMS},
            'paired_comparisons': [{'opponent': arm, 'paired_cases': 1, 'pack_only': [], 'opponent_only': [],
                                    'p_exact': 1.0, 'p_holm': 1.0} for arm in verifier.ARMS[1:]],
            'supported_superiority_in_this_experiment': False}


def test_luna_verifier_accepts_valid_record_and_rejects_partial_as_full(report):
    assert verifier.verify(report, case_ids=['T39'])['verified']
    with pytest.raises(ValueError):
        verifier.verify(report)


@pytest.mark.parametrize('change', ['source', 'duplicate', 'answer_type', 'score', 'receipt',
                                   'unchecked', 'skill', 'budget', 'model', 'superiority'])
def test_luna_verifier_rejects_forged_evidence(report, change):
    report = copy.deepcopy(report)
    row = report['results'][0]
    if change == 'source':
        report['source_sha256'].pop(next(iter(report['source_sha256'])))
    elif change == 'duplicate':
        report['results'].append(row)
    elif change == 'answer_type':
        row['answer']['answer']['executed'] = 0  # JSON number is not a boolean.
    elif change == 'score':
        row['passed'] = False
    elif change == 'receipt':
        row['receipts'] = [{'topic': 'invented', 'ok': True}]
    elif change == 'unchecked':
        row['calls'] = [{'name': 'mcp__contract__check_read_command', 'input': {'command': 'oci iam region list --query data'}, 'result_success': True}]
    elif change == 'skill':
        row['loaded_skills'] = ['unobserved']
    elif change == 'budget':
        report['protocol']['max_actions_per_case'] = 99
    elif change == 'model':
        report['model'] = 'different-model'
    else:
        report['supported_superiority_in_this_experiment'] = True
    with pytest.raises(ValueError):
        verifier.verify(report, case_ids=['T39'])


def test_four_discordant_wins_do_not_establish_significance():
    rows = [{'case': f'T{i:02}', 'arm': arm, 'passed': arm == 'pack'}
            for i in range(1, 5) for arm in verifier.ARMS]
    result = verifier.paired(rows, [f'T{i:02}' for i in range(1, 5)])
    assert all(c['p_exact'] == .125 and c['p_holm'] == .25 for c in result)
