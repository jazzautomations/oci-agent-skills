"""Limit metadata must never replace compartment quota scope or physical-capacity evidence."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def capacity():
    spec = importlib.util.spec_from_file_location('capacity_scope_test', ROOT / 'skills/oci-support-limits/scripts/capacity.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('scope', ['GLOBAL', 'REGION', 'AD'])
def test_metadata_scope_does_not_replace_child_quota_scope(capacity, monkeypatch, scope):
    from lib.oci_ro import prepare
    calls = []

    def fake(argv, **kwargs):
        # Exercise the real read policy too; no CLI or cloud process is run.
        assert kwargs['sanitize'] == (argv[1] != 'definition')
        prepared = prepare(argv, profile=kwargs['profile'], region=kwargs['region'])
        calls.append(prepared)
        data = [{'name': 'test-limit', 'scope': scope}] if argv[1] == 'definition' else {'available': 0}
        return {'ok': True, 'data': data, 'truncated': False}

    monkeypatch.setattr(capacity, 'run', fake)
    report = capacity.collect('TEST', 'test-region', 'test-tenancy', 'test-child', 'compute', 'test-limit', 'test-ad')
    assert report['ok'] and report['physical_capacity_verified'] is False
    assert report['compartment_headroom']['data']['available'] == 0
    assert [argv[argv.index('--compartment-id') + 1] for argv in calls] == ['test-tenancy', 'test-tenancy', 'test-child']
    for argv in calls[1:]:
        assert ('--availability-domain' in argv) == (scope == 'AD')
        if scope == 'AD':
            assert argv[argv.index('--availability-domain') + 1] == 'test-ad'
    assert all(argv[argv.index('--profile') + 1] == 'TEST' and argv[argv.index('--region') + 1] == 'test-region' for argv in calls)


@pytest.mark.parametrize('definition', [
    {'ok': False, 'data': []},
    {'ok': True, 'data': []},
    {'ok': True, 'data': 'invalid'},
    {'ok': True, 'data': [{'name': 'other', 'scope': 'AD'}]},
    {'ok': True, 'data': [{'name': 'test-limit', 'scope': 'unknown'}]},
    {'ok': True, 'data': [{'name': 'test-limit', 'scope': 'REGION'}], 'truncated': True},
    {'ok': True, 'data': [{'name': 'test-limit', 'scope': 'AD'}]},
])
def test_missing_or_ambiguous_scope_stops_before_further_calls(capacity, monkeypatch, definition):
    calls = []
    monkeypatch.setattr(capacity, 'run', lambda argv, **kwargs: calls.append(argv) or definition)
    with pytest.raises(ValueError):
        capacity.collect('TEST', 'test-region', 'test-tenancy', 'test-child', 'compute', 'test-limit')
    assert len(calls) == 1


def test_missing_child_never_falls_back_to_tenancy(capacity, monkeypatch):
    monkeypatch.setattr(capacity, 'run', lambda *args, **kwargs: pytest.fail('No read is allowed before explicit scope'))
    with pytest.raises(ValueError):
        capacity.collect('TEST', 'test-region', 'test-tenancy', '', 'compute', 'test-limit')


def test_failed_headroom_remains_unknown(capacity, monkeypatch):
    responses = iter([
        {'ok': True, 'data': [{'name': 'test-limit', 'scope': 'REGION'}]},
        {'ok': True, 'data': [{'value': 10}]},
        {'ok': False, 'error': {'kind': 'service', 'status': 404}},
    ])
    monkeypatch.setattr(capacity, 'run', lambda *args, **kwargs: next(responses))
    report = capacity.collect('TEST', 'test-region', 'test-tenancy', 'test-child', 'compute', 'test-limit')
    assert report['ok'] is False
    assert 'data' not in report['compartment_headroom']
    assert report['physical_capacity_verified'] is False
