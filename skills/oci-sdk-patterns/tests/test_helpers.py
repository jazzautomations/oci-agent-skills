"""Auth probes must honor selection; public spec paths remain fixed-origin."""
import argparse
import importlib.util
from pathlib import Path
import pytest


def module(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).parents[1] / ('scripts/' + name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def test_probe_forwards_auth_config_profile_region(monkeypatch):
    auth = module('verify_auth')
    calls = []
    def read(argv, **kwargs):
        calls.append((argv, kwargs))
        return {'ok': True}
    monkeypatch.setattr(auth, 'run', read)
    args = argparse.Namespace(auth='security_token', config='/tmp/example-config', profile='selected')
    assert auth.probe(['iam', 'region', 'list'], args, 'selected-region')['ok']
    argv, kwargs = calls[0]
    assert argv[-4:] == ['--auth', 'security_token', '--config-file', '/tmp/example-config']
    assert kwargs == {'profile': 'selected', 'region': 'selected-region'}


def test_missing_config_does_not_guess_instance_principal(tmp_path):
    assert module('verify_auth').section(tmp_path / 'missing', 'selected') is None


def test_spec_resolution_rejects_non_hash_paths():
    fetch = module('fetch_spec')
    assert fetch.resolve({'specs': ['./specs/' + 'a' * 64 + '.yaml']}) == [fetch.ORIGIN + 'a' * 64 + '.yaml']
    for path in ['../config', 'https://example.com/spec.yaml', './specs/not-a-hash.yaml']:
        with pytest.raises(ValueError):
            fetch.resolve({'specs': [path]})
