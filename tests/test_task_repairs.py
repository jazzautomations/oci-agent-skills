"""Run actual authored projections on CLI-shaped data; not model or live certification."""
import json
from pathlib import Path
import shlex
import sys

import jmespath
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/ci'))
sys.path.insert(0, str(ROOT / 'scripts'))
from lint_fences import commands
from read_contract import check


def proposal(skill, prefix):
    matches = [command for _, command in commands((ROOT / 'skills' / skill / 'SKILL.md').read_text())
               if command.startswith(prefix)]
    assert len(matches) == 1
    assert check(matches[0])['valid']
    argv = shlex.split(matches[0])
    return matches[0], argv[argv.index('--query') + 1]


def test_policy_projection_excludes_nonfindings_and_preserves_observed_statements():
    _, query = proposal('oci-security-posture', 'oci iam policy list')
    records = {'data': [
        {'name': 'readers', 'statements': ['Allow group Readers to inspect instances in compartment dev']},
        {'name': 'public-read', 'statements': ['Allow any-user to inspect instances in compartment dev']},
        {'name': 'mixed', 'statements': ['Allow group Admins to manage all-resources in tenancy',
                                        'Allow group Readers to inspect instances in compartment dev']}]}
    result = jmespath.search(query, records)
    assert result == [{'n': 'public-read', 'broad': [records['data'][1]['statements'][0]]},
                      {'n': 'mixed', 'broad': [records['data'][2]['statements'][0]]}]
    assert jmespath.search(query, {'data': records['data'][:1]}) == []


def test_default_route_projection_excludes_isolated_and_nondefault_routes():
    _, query = proposal('oci-networking', 'oci network route-table list')
    private = {'destination': '10.4.0.0/16', 'network-entity-id': 'private-target'}
    ipv4 = {'destination': '0.0.0.0/0', 'network-entity-id': 'ipv4-target'}
    ipv6 = {'destination': '::/0', 'network-entity-id': 'ipv6-target'}
    result = jmespath.search(query, {'data': [
        {'display-name': 'isolated', 'route-rules': []},
        {'display-name': 'private', 'route-rules': [private]},
        {'display-name': 'dual-stack', 'route-rules': [private, ipv4, ipv6]}]})
    assert result == [{'name': 'dual-stack', 'routes': [ipv4, ipv6]}]


def test_subscription_and_budget_proposals_are_bounded_projected_reads():
    command, _ = proposal('oci-cli-auth', 'oci iam region-subscription list')
    assert '--all' not in shlex.split(command)
    proposal('oci-cost-analysis', 'oci budgets budget budget list')


def test_default_route_catalog_example_is_shape_only_not_new_live_authority():
    from check_examples import PLACEHOLDERS, live_argv
    rows = json.loads((ROOT / 'catalog/fragments/oci-networking.json').read_text())
    example = next(r for r in rows if r['id'] == 'oci-networking-default-routes')
    assert example['live'] is False and 'VCN_ID' in PLACEHOLDERS
    with pytest.raises(ValueError, match='live allowlist'):
        live_argv(example, 'network route-table list', {}, {}, {})


def test_final_metrics_query_edit_invalidates_exact_observed_check():
    sys.path.insert(0, str(ROOT / 'scripts/eval'))
    from checked_task_benchmark import score
    command, _ = proposal('oci-monitoring-alarms', 'oci monitoring metric-data summarize-metrics-data')
    edited = command.replace('"$MQL"', '"CpuUtilization[1h].mean()"')
    fixture = {'topic': 'metrics', 'expected': {'mean': 7}}
    calls = [{'name': 'mcp__contract__check_read_command', 'input': {'command': command}, 'result_success': True}]
    answer = {'answer': {'mean': 7}, 'commands': [edited]}
    receipts = [{'topic': 'metrics', 'ok': True}]
    assert not score(fixture, answer, receipts, calls)['passed']
    calls.append({'name': 'mcp__contract__check_read_command', 'input': {'command': edited}, 'result_success': True})
    assert score(fixture, answer, receipts, calls)['passed']
