"""Regression checks for exposure severity and safe report identifiers."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('posture', Path(__file__).parents[1] / 'scripts/posture.py')
posture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(posture)


def test_admin_ports_inside_ranges_and_ipv6(monkeypatch):
    rules = [dict(source='0.0.0.0/0', protocol='6', **{'tcp-options': {'destination-port-range': {'min': 1, 'max': 1024}}}),
             dict(source='::/0', protocol='all'),
             dict(source='0.0.0.0/0', protocol='6', **{'tcp-options': {'destination-port-range': {'min': 80, 'max': 80}}})]
    monkeypatch.setattr(posture, 'read', lambda *args: [dict(n='private-label', r=rules)])
    findings = []
    posture.ingress('scope', findings, [], [])
    assert [r['severity'] for r in findings] == ['CRITICAL', 'CRITICAL', 'HIGH']
    assert all(r['resource'].startswith('sha256:') for r in findings)
    assert 'private-label' not in str(findings)


def test_age_parser_handles_invalid_or_naive_timestamps():
    assert posture.age_days('bad') is None
    assert posture.age_days('2026-01-01T00:00:00') is None
