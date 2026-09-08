#!/usr/bin/env python3
"""Build Console links without network access; detail routes are conventions."""
import argparse
import configparser
import json
import os
import re
from pathlib import Path
from urllib.parse import quote, urlencode

REGIONS = json.loads(Path(__file__).with_name('console_regions.json').read_text())
TYPE_SEGMENT = {
    'instance': 'compute/instances', 'vcn': 'networking/vcns',
    'autonomousdatabase': 'db/adb', 'cluster': 'containers/clusters',
    'alarm': 'monitoring/alarms', 'ormstack': 'resourcemanager/stacks',
    'policy': 'identity/policies', 'compartment': 'identity/compartments',
    'user': 'identity/users', 'group': 'identity/groups', 'tenancy': '',
    'volume': 'block-storage/volumes', 'subnet': '', 'bucket': '',
}
IDENTITY = {'policy', 'compartment', 'user', 'group', 'tenancy'}


def parse_ocid(ocid):
    if not isinstance(ocid, str) or not re.fullmatch(r'ocid1\.[a-z][a-z0-9]*\.[a-z0-9]+\.[a-z0-9-]*\.[A-Za-z0-9._-]+', ocid):
        raise ValueError('Invalid OCID: expected ocid1.type.realm.region.unique')
    parts = ocid.split('.')
    return parts[1], parts[3], parts[2]


def is_verified(kind):
    # Only the tenancy landing page is a verified literal, not a detail convention.
    return kind == 'tenancy'


def build(ocid=None, *, kind=None, region=None, compartment_id=None,
          namespace=None, bucket=None, parent_ocid=None, tab=None, fallback_region=None):
    airport = ''
    warnings = []
    if ocid:
        parsed_kind, airport, realm = parse_ocid(ocid)
        if realm != 'oc1':
            raise ValueError('Only the commercial Console realm is mapped')
        if kind and kind != parsed_kind:
            raise ValueError('Kind does not match OCID')
        kind = parsed_kind
    if kind not in TYPE_SEGMENT:
        raise ValueError('Unmapped resource type')
    resolved = None if kind in IDENTITY else region or REGIONS.get(airport.lower()) or fallback_region
    if kind not in IDENTITY and not resolved:
        warnings.append('Region absent; Console may select its last-used region.')
    if not is_verified(kind):
        warnings.append('Detail route is a convention; confirm in browser.')
    def esc(value):
        return quote(value, safe='')
    if kind == 'bucket':
        if not namespace or not bucket:
            raise ValueError('Bucket requires namespace and bucket name')
        path = f'object-storage/buckets/{esc(namespace)}/{esc(bucket)}/objects'
    elif kind == 'subnet':
        if not parent_ocid or parse_ocid(parent_ocid)[0] != 'vcn':
            raise ValueError('Subnet requires parent VCN OCID')
        path = f'networking/vcns/{esc(parent_ocid)}/subnets/{esc(ocid)}'
    elif kind == 'tenancy':
        path = ''
    else:
        if not ocid:
            raise ValueError('Resource requires OCID')
        path = f'{TYPE_SEGMENT[kind]}/{esc(ocid)}'
    if tab:
        if tab in {'.', '..'}:
            raise ValueError('Invalid tab')
        path += '/' + esc(tab)
    params = []
    if resolved:
        params.append(('region', resolved))
    if compartment_id:
        params.append(('compartmentId', compartment_id))
    url = 'https://cloud.oracle.com/' + path
    if params:
        url += '?' + urlencode(params)
    return {'url': url, 'kind': kind, 'region': resolved, 'verified': is_verified(kind), 'warnings': warnings}


def console_url(ocid=None, **kwargs):
    return build(ocid, **kwargs)['url']


def configured_region():
    if os.environ.get('OCI_CLI_REGION'):
        return os.environ['OCI_CLI_REGION']
    config = configparser.ConfigParser()
    try:
        config.read(os.environ.get('OCI_CLI_CONFIG_FILE', os.path.expanduser('~/.oci/config')))
        return config.get(os.environ.get('OCI_CLI_PROFILE', 'DEFAULT'), 'region', fallback=None)
    except (OSError, configparser.Error):
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('ocid', 'kind', 'region', 'compartment-id', 'namespace', 'bucket', 'parent-ocid', 'tab'):
        parser.add_argument('--' + name)
    parser.add_argument('--json', action='store_true')
    args = vars(parser.parse_args())
    as_json = args.pop('json')
    try:
        result = build(**args, fallback_region=configured_region())
    except ValueError as exc:
        parser.error(str(exc))
    if as_json:
        print(json.dumps(result, sort_keys=True))
    else:
        import sys
        print(result['url'])
        for warning in result['warnings']:
            print(warning, file=sys.stderr)


if __name__ == '__main__':
    main()
