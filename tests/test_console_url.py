import sys
from pathlib import Path
from urllib.parse import urlsplit

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from console_url import build, console_url


@pytest.mark.parametrize('airport,region', [('ord', 'us-chicago-1'), ('iad', 'us-ashburn-1')])
def test_console_airport_and_order(airport, region):
    result = build(f'ocid1.instance.oc1.{airport}.example', compartment_id='example')
    assert result['url'].endswith(f'?region={region}&compartmentId=example')
    assert not result['verified'] and result['warnings']
    assert urlsplit(result['url']).hostname == 'cloud.oracle.com'
    assert build(f'ocid1.instance.oc1.{airport}.example', region='override')['region'] == 'override'


def test_console_identity_bucket_subnet_and_unknown():
    assert '?' not in console_url('ocid1.policy.oc1..example', region='us-chicago-1')
    assert build('ocid1.instance.oc1.zzz.example')['region'] is None
    assert build('ocid1.instance.oc1.zzz.example', fallback_region='fallback')['region'] == 'fallback'
    assert '/ns/bucket%2Fname/objects' in console_url(kind='bucket', namespace='ns', bucket='bucket/name')
    assert '/subnets/' in console_url('ocid1.subnet.oc1.ord.example', parent_ocid='ocid1.vcn.oc1.ord.example')
    for kwargs in [{'ocid': 'ocid1.unknown.oc1..example'}, {'ocid': 'invalid'},
                   {'ocid': 'ocid1.instance.oc1'}, {'kind': 'bucket', 'bucket': 'name'},
                   {'ocid': 'ocid1.subnet.oc1.ord.example'}, {'ocid': 'ocid1.instance.oc2.iad.example'}]:
        with pytest.raises(ValueError):
            build(**kwargs)
