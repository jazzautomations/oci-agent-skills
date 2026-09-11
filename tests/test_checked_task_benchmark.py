from pathlib import Path
import copy
import json
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/eval'))
import checked_task_benchmark as benchmark
import verify_checked_task_benchmark as verifier


def test_alias_requires_unique_registration_and_loaded_body():
    names = ['oci-agent-skills:oci-compute']
    assert benchmark.resolve_skill('oci-compute', names, ['oci-compute']) == names[0]
    assert benchmark.resolve_skill('oci-compute', names, []) is None
    assert benchmark.resolve_skill('oci-compute', names + ['other:oci-compute'], ['oci-compute']) is None
    assert benchmark.resolve_skill('other:oci-compute', names, ['oci-compute']) is None


def test_contract_receipt_is_required_in_addition_to_valid_final_command():
    fixture = {'topic': 'synthetic', 'expected': {'count': 0}}
    answer = {'answer': {'count': 0}, 'commands': ['oci iam region list --query data']}
    receipts = [{'topic': 'synthetic', 'ok': True}]
    assert not benchmark.score(fixture, answer, receipts, [])['passed']
    calls = [{'name': 'mcp__contract__check_read_command', 'input': {'command': answer['commands'][0]}, 'result_success': True}]
    assert benchmark.score(fixture, answer, receipts, calls)['passed']


def test_contract_does_not_replace_original_exact_answer_criterion():
    fixture = {'topic': None, 'expected': {'review': True}}
    assert not benchmark.score(fixture, {'answer': {'review': False}, 'commands': []}, [], [])['passed']


@pytest.fixture
def report():
    return json.loads((ROOT / 'evals/results/checked-task-benchmark-2026-09-11.json').read_text())


def test_checked_task_evidence(report):
    assert verifier.verify(report)['verified']


@pytest.mark.parametrize('mutation', ['source', 'pair', 'cost', 'checked', 'alias', 'tools', 'launch'])
def test_checked_task_evidence_rejects_tampering(report, mutation):
    report = copy.deepcopy(report)
    row = next(r for r in report['results'] if r['completed'] and r['answer']['commands'] and r['arm'] == 'native-plugin')
    if mutation == 'source':
        report['source_sha256'].pop(next(iter(report['source_sha256'])))
    elif mutation == 'pair':
        report['results'].append(row)
    elif mutation == 'cost':
        report['reported_cost_usd'] += 1
    elif mutation == 'checked':
        row['each_final_command_checked'] = not row['each_final_command_checked']
    elif mutation == 'alias':
        row['skill_resolutions'].append({'requested': 'foreign', 'canonical': 'oci-agent-skills:foreign', 'result_success': True})
    elif mutation == 'tools':
        row['initialized_tools'].append('Bash')
    else:
        row['launch_options'] += ['--allowedTools', 'Read']
    with pytest.raises(ValueError):
        verifier.verify(report)
