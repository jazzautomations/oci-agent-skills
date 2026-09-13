#!/usr/bin/env python3
"""Read service-limit metadata and explicit compartment headroom; never launch resources."""
import argparse
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts'))
from lib.oci_ro import run
from lib.sanitize import emit


def collect(profile, region, tenancy, compartment, service, limit_name, ad=None):
    if not all(isinstance(value, str) and value.strip() for value in
               (profile, region, tenancy, compartment, service, limit_name)):
        raise ValueError('Explicit profile, region, tenancy, compartment, service and limit are required')

    def read(argv, *, inspect_scope=False):
        return run(argv, profile=profile, region=region, sanitize=not inspect_scope)

    definition = read(['limits', 'definition', 'list', '--compartment-id', tenancy,
                       '--service-name', service, '--name', limit_name, '--limit', '2',
                       '--query', 'data[].{name:name,scope:"scope-type"}'], inspect_scope=True)
    rows = definition.get('data')
    if (not definition.get('ok') or definition.get('truncated') or not isinstance(rows, list)
            or len(rows) != 1 or not isinstance(rows[0], dict)
            or rows[0].get('name') != limit_name or rows[0].get('scope') not in ('GLOBAL', 'REGION', 'AD')):
        raise ValueError('The exact limit scope could not be established; no headroom read was made')
    scope = rows[0]['scope']
    if scope == 'AD' and (not isinstance(ad, str) or not ad.strip()):
        raise ValueError('AD is required for this AD-scoped limit; no headroom read was made')
    ad_flags = ['--availability-domain', ad] if scope == 'AD' else []
    values = read(['limits', 'value', 'list', '--compartment-id', tenancy,
                   '--service-name', service, '--name', limit_name, '--scope-type', scope,
                   *ad_flags, '--limit', '2',
                   '--query', 'data[].{name:name,value:value,ad:"availability-domain"}'])
    headroom = read(['limits', 'resource-availability', 'get', '--compartment-id', compartment,
                     '--service-name', service, '--limit-name', limit_name, *ad_flags,
                     '--query', 'data'])
    return {'ok': bool(values.get('ok') and headroom.get('ok')),
            'scope_type': scope, 'configured_values': values, 'compartment_headroom': headroom,
            'physical_capacity_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__, epilog=
        'Env: PROFILE REGION TENANCY_ID COMPARTMENT_ID SERVICE LIMIT_NAME required. '
        'AD is required only for AD-scoped limits and omitted for GLOBAL/REGION. '
        'TENANCY_ID scopes metadata; COMPARTMENT_ID scopes quota/usage headroom. '
        'Output is one JSON report, not a physical-capacity guarantee.')
    parser.parse_args()
    keys = ('PROFILE', 'REGION', 'TENANCY_ID', 'COMPARTMENT_ID', 'SERVICE', 'LIMIT_NAME')
    if not all(os.environ.get(key) for key in keys):
        parser.error('Set ' + ', '.join(keys) + ' explicitly')
    try:
        report = collect(*(os.environ[key] for key in keys), os.environ.get('AD'))
    except ValueError as error:
        print(emit({'ok': False, 'error': str(error)}))
        return 1
    print(emit(report))
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
