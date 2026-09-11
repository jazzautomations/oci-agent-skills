"""Regression checks for ordered, read-only incident evidence."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('triage', Path(__file__).parents[1] / 'scripts/triage.py')
triage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(triage)


def test_read_events_are_not_mutation_candidates():
    for method, event in [('GET', 'GetSubnet'), ('POST', 'ListInstances'),
                          ('HEAD', 'HeadObject'), ('POST', 'SummarizeMetricsData'),
                          ('GET', 'ServiceApi'), ('', 'LaunchInstance.begin')]:
        assert not triage.mutation_candidate({'method': method, 'k': 'com.oraclecloud.' + event})
    assert triage.mutation_candidate({'method': 'POST', 'k': 'com.oraclecloud.compute.LaunchInstance.begin'})


def test_ten_reads_in_order_and_failed_steps_remain_gaps(monkeypatch):
    calls = []
    def read(argv, **kwargs):
        calls.append(argv)
        if argv[0] == 'cloud-guard':
            return {'ok': False, 'error': {'kind': 'service', 'status': 404}}
        return {'ok': True, 'data': [], 'truncated': False}
    monkeypatch.setattr(triage, 'run', read)
    result = triage.sweep(dict(profile='test', region='test', compartment='compartment',
                              tenancy='tenancy', instance='instance', user='user', start='start', end='end'))
    assert [r['step'] for r in result] == list(range(1, 11))
    assert len(calls) == 11
    assert calls[1][:3] == ['audit', 'event', 'list']
    assert calls[6][:3] == ['compute', 'instance', 'get']
    assert calls[9][calls[9].index('--compartment-id') + 1] == 'tenancy'
    assert result[2]['ok'] is False
    assert 'rows' not in result[2]


def test_disabled_cloud_guard_is_diagnosed_without_hiding_failure(monkeypatch):
    def read(argv, **kwargs):
        if argv[1] == 'problem':
            return {'ok': False, 'error': {'kind': 'service', 'status': 404}}
        assert argv == ['cloud-guard', 'configuration', 'get', '--compartment-id', 'tenancy']
        assert kwargs['attempts'] == 1
        return {'ok': True, 'data': {'data': {'status': 'DISABLED', 'reporting-region': None}}}
    monkeypatch.setattr(triage, 'run', read)
    result = triage.step(3, 'cloud-guard', ['cloud-guard', 'problem', 'list'],
                         dict(profile='test', region='test', tenancy='tenancy'))
    assert result['ok'] is False and 'rows' not in result
    assert result['diagnostic']['state'] == 'DISABLED'
    assert result['diagnostic']['reporting_region_matches'] is None


def test_configuration_malformed_response_is_unknown(monkeypatch):
    for data in (None, [], {'data': []}, {'data': {'status': 'unexpected'}}):
        monkeypatch.setattr(triage, 'run', lambda *a, **k: {'ok': True, 'data': data})
        assert triage.cloud_guard_configuration(dict(profile='test', region='test', tenancy='tenancy')) == {'state': 'unknown'}


def test_enabled_configuration_does_not_establish_problem_coverage(monkeypatch):
    monkeypatch.setattr(triage, 'run', lambda *a, **k: {'ok': True, 'data': {'data': {
        'status': 'ENABLED', 'reporting-region': 'another-region'}}})
    result = triage.cloud_guard_configuration(dict(profile='test', region='test', tenancy='tenancy'))
    assert result['reporting_region_matches'] is False
    assert 'unknown' in result['action']


def test_support_requires_user_context_without_an_unscoped_call(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('No Support request without an explicit user')
    monkeypatch.setattr(triage, 'run', forbidden)
    result = triage.support_step({'profile': 'test', 'region': 'test', 'tenancy': 'tenancy'})
    assert not result['ok'] and result['error']['kind'] == 'missing_user_context'


def test_support_uses_user_domain_home_region_and_array_projection(monkeypatch):
    calls = []
    def read(argv, **kwargs):
        calls.append(argv)
        return {'ok': True, 'data': [{'key': 'synthetic-one'}, {'key': 'synthetic-two'}], 'truncated': False}
    monkeypatch.setattr(triage, 'run', read)
    scope = dict(profile='test', region='selected', tenancy='tenancy', user='user',
                 home_region='home', identity_domain='domain')
    result = triage.support_step(scope)
    assert result['ok'] and result['rows'] == 2
    argv = calls[0]
    for flag, value in [('--ocid', 'user'), ('--homeregion', 'home'), ('--domainid', 'domain')]:
        assert argv[argv.index(flag) + 1] == value
    assert argv[argv.index('--query') + 1] == 'data[].{key:key}'


def test_support_403_is_preserved_without_an_entitlement_inference(monkeypatch):
    monkeypatch.setattr(triage, 'run', lambda *a, **kw: {'ok': False, 'error': {'kind': 'service', 'status': 403}})
    result = triage.support_step(dict(profile='test', region='test', tenancy='tenancy', user='user'))
    assert not result['ok'] and 'rows' not in result
    assert result['diagnostic']['entitlement_established'] is False
