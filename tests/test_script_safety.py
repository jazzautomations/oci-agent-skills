"""Structural and bounded-page regressions; subprocess results are local fixtures."""
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
sys.path.insert(0, str(ROOT/'scripts/ci'))
from check_scripts_readonly import validate
from lib import oci_ro


def test_wrapper_import_must_be_called(tmp_path):
    path = tmp_path/'skills/example/scripts/read.py'
    path.parent.mkdir(parents=True)
    for text in ['# oci_ro\n', 'from lib.oci_ro import run\n', 'from lib import oci_ro\n']:
        path.write_text(text)
        assert any(f['code'] == 'missing_wrapper' for f in validate(path, tmp_path))
    path.write_text('from lib.oci_ro import run as read\nread([])\n')
    assert not validate(path, tmp_path)
    path.write_text('from lib import oci_ro as wrapper\nwrapper.run([])\n')
    assert not validate(path, tmp_path)


@pytest.mark.parametrize('payload', ['[{},{}]', '{"data":[{},{}]}', '{"data":{"items":[{},{}]}}'])
def test_wrapper_flags_page_saturation(monkeypatch, payload):
    monkeypatch.setattr(oci_ro, 'run_process', lambda *a, **k:SimpleNamespace(returncode=0,stdout=payload,stderr=''))
    result = oci_ro.run(['compute','instance','list','--compartment-id','example','--limit','2'],sanitize=False)
    assert result['ok'] and result['truncated'] and result['page_saturated']


def test_filtered_page_keeps_pagination_warning(monkeypatch):
    monkeypatch.setattr(oci_ro,'run_process',lambda *a,**k:SimpleNamespace(returncode=0,stdout='[]',stderr='WARNING: not all resources were returned.'))
    assert oci_ro.run(['compute','instance','list','--compartment-id','example','--limit','2'])['truncated']


def test_smoke_scope_refuses_broader_reads(monkeypatch):
    monkeypatch.setenv('OCI_RO_SMOKE_SCOPE','example')
    monkeypatch.setenv('OCI_RO_SMOKE_PROFILE','TEST')
    monkeypatch.setenv('OCI_RO_SMOKE_REGION','us-ashburn-1')
    for tail in [['--compartment-id','other'], ['--compartment-id','example','--all']]:
        with pytest.raises(oci_ro.ReadOnlyRefusal):
            oci_ro.prepare(['iam','compartment','list',*tail],profile='TEST',region='us-ashburn-1')


def test_certificate_cap_is_twenty():
    spec = importlib.util.spec_from_file_location('cert_expiry',ROOT/'skills/oci-vault-certificates/scripts/cert_expiry.py')
    module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    from datetime import datetime,timezone
    with pytest.raises(ValueError):
        module.summarize([{}]*20,datetime.now(timezone.utc),30)
