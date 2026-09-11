import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/eval'))
import native_reference_benchmark as benchmark
import export_skill_creator_review as exporter
import verify_native_reference_benchmark as verifier


def test_read_scope_rejects_escape_and_fixture(tmp_path):
    plugin = tmp_path / 'plugin'
    (plugin / 'skills').mkdir(parents=True)
    (plugin / 'skills/escape').symlink_to(tmp_path)
    assert benchmark.approved_read(plugin / 'skills/domain/SKILL.md', plugin)
    assert benchmark.approved_read(plugin / 'references/guide.md', plugin)
    assert not benchmark.approved_read(plugin / 'evals/tasks.json', plugin)
    assert not benchmark.approved_read(plugin / 'skills/../../secret', plugin)
    assert not benchmark.approved_read(plugin / 'skills/escape/secret', plugin)


def test_host_never_adds_whole_plugin_or_enables_executor(tmp_path):
    plugin = tmp_path / 'plugin'
    options = benchmark.native_options(plugin, tmp_path / 'session')
    additional = options[options.index('--add-dir') + 1:options.index('--allowedTools')]
    assert additional == [str(plugin / 'skills'), str(plugin / 'references')]
    assert options[options.index('--tools') + 1] == 'Skill,Read'
    assert f'Read(/{plugin}/evals/**)' in options


def test_budget_reserves_concurrent_overshoot_and_unknown_cost_stops():
    assert benchmark.can_admit([], 2, .5)
    assert not benchmark.can_admit([{'cost_usd': .1}], 2, .59)
    assert not benchmark.can_admit([{}], 1, 6)
    assert not benchmark.can_admit([{'cost_usd': float('nan')}], 1, 6)


def test_all_readable_sources_are_bound_and_prior_collector_preserved():
    paths = benchmark.source_paths()
    assert ROOT / 'scripts/eval/native_task_benchmark.py' in paths
    assert ROOT / 'references/service-command-cards.md' in paths
    assert ROOT / 'skills/oci-cost-analysis/references/usage-api.md' in paths


def test_private_paths_are_normalized(tmp_path):
    assert benchmark.normalize({'path': f'{tmp_path}/plugin/references/a.md'},
                               tmp_path / 'plugin', tmp_path / 'session') == {
                                   'path': '$PLUGIN/references/a.md'}


def test_token_accounting_includes_cache_without_character_surrogate():
    assert exporter.total_tokens({'input_tokens': 10, 'output_tokens': 20,
        'cache_creation_input_tokens': 30, 'cache_read_input_tokens': 40}) == 100


def test_grading_is_one_conjunctive_task_not_easy_subcheck_average():
    row = {'completed': True, 'passed': True, 'answer_correct': True,
           'required_evidence_read': True, 'calls': [],
           'native_skill_activated': False, 'successful_reference_reads': 0}
    grade = exporter.grading(row, {'recomputed_passed': False,
                                  'commands': [{'valid': False}]})
    assert grade['summary'] == {'passed': 0, 'failed': 1, 'total': 1, 'pass_rate': 0}
    assert not grade['expectations'][0]['passed']


@pytest.fixture
def recorded_report():
    return json.loads((ROOT / 'evals/results/native-reference-benchmark-2026-09-11.json').read_text())


def test_recorded_reference_evidence(recorded_report):
    assert verifier.verify(recorded_report)['verified']
    summary = json.loads((ROOT / 'evals/results/native-reference-skill-creator-2026-09-11.json').read_text())
    audit_path = ROOT / 'evals/results/native-reference-command-audit-2026-09-11.json'
    audit = json.loads(audit_path.read_text())
    assert summary['metadata']['source_report_sha256'] == audit['source_report_sha256']
    assert summary['metadata']['audit_sha256'] == hashlib.sha256(audit_path.read_bytes()).hexdigest()
    assert summary['metadata']['runs_per_configuration'] == 1
    assert summary['metadata']['executor_model'] == benchmark.MODEL
    assert len(summary['runs']) == 80
    records = {(r['case'], r['arm']): r for r in recorded_report['results']}
    audits = {(r['case'], r['arm']): r for r in audit['results']}
    seen = set()
    for run in summary['runs']:
        key = (f"T{run['eval_id']:02d}", 'native-plugin' if run['configuration'] == 'with_skill' else 'without-plugin')
        assert key not in seen
        seen.add(key)
        row = records[key]
        grade = exporter.grading(row, audits[key])
        assert run['expectations'] == grade['expectations']
        assert run['result']['pass_rate'] == grade['summary']['pass_rate']
        assert run['result']['time_seconds'] == row['duration_ms'] / 1000
        assert run['result']['tokens'] == exporter.total_tokens(row['usage'])
    for config, arm in [('with_skill', 'native-plugin'), ('without_skill', 'without-plugin')]:
        assert summary['run_summary'][config]['pass_rate']['mean'] == audit['arms'][arm]['passed'] / 40


@pytest.mark.parametrize('mutation', ['pair', 'source', 'cost', 'tools', 'grant', 'grade', 'read'])
def test_recorded_reference_evidence_rejects_tampering(recorded_report, mutation):
    report = copy.deepcopy(recorded_report)
    row = next(r for r in report['results'] if r['completed'] and r['arm'] == 'native-plugin')
    if mutation == 'pair':
        report['results'].append(row)
    elif mutation == 'source':
        report['source_sha256'].pop(next(iter(report['source_sha256'])))
    elif mutation == 'cost':
        report['reported_cost_usd'] += 1
    elif mutation == 'tools':
        row['initialized_tools'].append('Bash')
    elif mutation == 'grant':
        row['launch_options'] += ['--allowedTools', 'Read']
    elif mutation == 'grade':
        row['passed'] = not row['passed']
    else:
        row['successful_reference_reads'] += 1
    with pytest.raises(ValueError):
        verifier.verify(report)
