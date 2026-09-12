"""A failed refresh must not make old or incomplete cloud facts look current."""
from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from lib import pricing

spec = importlib.util.spec_from_file_location('freshness', ROOT / 'scripts/ci/check_cloud_freshness.py')
freshness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(freshness)


def payload(age=0, currency='USD'):
    return {'lastUpdated': '2026-01-01', 'items': [], '_currency': currency,
            '_retrieved_at': (datetime.now(timezone.utc)-timedelta(hours=age)).isoformat()}


def no_network(*args, **kwargs):
    raise OSError('unavailable')


def test_recent_cache_and_explicit_offline_never_fetch(tmp_path, monkeypatch):
    cache = tmp_path/'prices.json'
    cache.write_text(json.dumps(payload()))
    monkeypatch.setattr(pricing, 'build_opener', no_network)
    assert pricing.load_prices(cache).snapshot == '2026-01-01'
    cache.write_text(json.dumps(payload(age=48)))
    assert pricing.load_prices(cache, offline=True).snapshot == '2026-01-01'
    with pytest.raises(OSError):
        pricing.load_prices(cache)
    with pytest.raises(ValueError, match='existing cache'):
        pricing.load_prices(tmp_path/'absent.json', offline=True)


@pytest.mark.parametrize('data', [payload(25), payload(-2), payload(currency='BRL'),
                                  {'lastUpdated':'old','items':[]}])
def test_stale_future_unstamped_and_wrong_currency_cache_refresh(tmp_path, monkeypatch, data):
    cache = tmp_path/'prices.json'
    cache.write_text(json.dumps(data))
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self, limit): return json.dumps({'lastUpdated':'new','items':[]}).encode()
    class Opener:
        def open(self, url, timeout): return Response()
    monkeypatch.setattr(pricing,'build_opener',lambda *args: Opener())
    book = pricing.load_prices(cache)
    assert book.snapshot == 'new' and book.retrieved_at
    assert json.loads(cache.read_text())['_currency'] == 'USD'


def test_price_watch_rejects_partial_response():
    with pytest.raises(ValueError, match='Incomplete'):
        freshness.summarize('oci_prices', '{"items":[]}')


def test_source_failure_cannot_be_reported_as_unchanged(monkeypatch):
    monkeypatch.setattr(freshness,'SOURCES',{'oci_cli':'https://pypi.org/pypi/oci-cli/json'})
    monkeypatch.setattr(freshness,'urlopen',no_network)
    current,gaps = freshness.collect()
    assert not current and gaps[0]['status']=='unavailable; not unchanged'
    changes = freshness.compare({'oci_cli':{'version':'1'}},{'oci_cli':{'version':'2'}})
    assert changes[0]['previous']['version']=='1' and changes[0]['current']['version']=='2'


def test_document_watch_ignores_script_and_whitespace():
    text = '<main>'+'Cloud contract. '*20+'</main>'
    assert freshness.summarize('oci_shapes',text)==freshness.summarize('oci_shapes',text+'<script>random()</script>\n')


def aws_reference(version='2.36.43'):
    banner = f'AWS CLI {version} Command Reference'
    return (f'<title>{banner}</title><nav>{banner}</nav><main>'
            'describe-instance-types --max-items 200 '
            'VCpuInfo DefaultVCpus DefaultCores DefaultThreadsPerCore '
            'MemoryInfo SizeInMiB 1024. Requires AWS CLI 2.36.43.'
            f'</main><footer>{banner}</footer>')


def test_aws_reference_ignores_only_banner_patch_release():
    old = aws_reference()
    new = aws_reference('2.36.44')
    assert freshness.summarize('aws_instance_contract',old)==freshness.summarize('aws_instance_contract',new)
    # This exception must not suppress versions in any other watched source.
    assert freshness.summarize('oci_shapes',old)!=freshness.summarize('oci_shapes',new)


@pytest.mark.parametrize('before,after', [
    ('DefaultVCpus','MaximumVCpus'), ('1024','2048'),
    ('--max-items 200','--max-items 100'),
    ('Requires AWS CLI 2.36.43','Requires AWS CLI 2.36.44'),
    ('AWS CLI 2.36.43 Command Reference','AWS CLI 2.37.0 Command Reference'),
    ('AWS CLI 2.36.43 Command Reference','AWS CLI 3.0.0 Command Reference'),
])
def test_aws_reference_still_detects_contract_changes(before,after):
    old = aws_reference()
    previous = {'aws_instance_contract':freshness.summarize('aws_instance_contract',old)}
    current = {'aws_instance_contract':freshness.summarize('aws_instance_contract',old.replace(before,after))}
    assert freshness.compare(previous,current)[0]['source']=='aws_instance_contract'
