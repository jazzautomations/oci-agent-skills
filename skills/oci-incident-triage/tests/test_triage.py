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
                              tenancy='tenancy', instance='instance', start='start', end='end'))
    assert [r['step'] for r in result] == list(range(1, 11))
    assert len(calls) == 10
    assert calls[1][:3] == ['audit', 'event', 'list']
    assert calls[5][:3] == ['compute', 'instance', 'get']
    assert calls[8][calls[8].index('--compartment-id') + 1] == 'tenancy'
    assert result[2]['ok'] is False
    assert 'rows' not in result[2]
