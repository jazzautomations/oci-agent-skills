#!/usr/bin/env python3
'''Read-only tenancy governance baseline: compartments, tags, quotas, budgets. Never mutates.'''
import argparse
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts'))
from lib.oci_ro import run
from lib.sanitize import clean, emit

LIMIT = '200'


def read(argv, profile, region):
    '''One bounded read. Returns None only when the call FAILED; an empty result is [].'''
    result = run(argv, profile=profile, region=region, sanitize=False)
    if not result.get('ok'):
        return None
    data = result.get('data')
    return data if isinstance(data, list) else []


def names(rows, key):
    return sorted({clean(row[key], 'tag_key')[0] for row in rows
                   if isinstance(row, dict) and isinstance(row.get(key), str)})


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog='Env: PROFILE, REGION, TENANCY_ID (root compartment) required; '
               'COMPARTMENT_ID optional, scopes the tag-default read. Bounded at 200 rows.')
    parser.parse_args()
    required = ('PROFILE', 'REGION', 'TENANCY_ID')
    if not all(os.environ.get(k) for k in required):
        parser.error('Set ' + ', '.join(required) + ' (TENANCY_ID is the root compartment)')
    profile, region = os.environ['PROFILE'], os.environ['REGION']
    root = os.environ['TENANCY_ID']
    scope = os.environ.get('COMPARTMENT_ID', root)

    compartments = read(['iam', 'compartment', 'list', '--compartment-id', root,
                         '--compartment-id-in-subtree', 'true', '--access-level', 'ANY',
                         '--limit', LIMIT, '--query', 'data[].{name:name}'], profile, region)
    namespaces = read(['iam', 'tag-namespace', 'list', '--compartment-id', root,
                       '--limit', LIMIT, '--query', 'data[].{name:name}'], profile, region)
    cost_tags = read(['iam', 'tag', 'list-cost-tracking', '--compartment-id', root,
                      '--limit', LIMIT,
                      '--query', 'data[].{name:join(\'.\',["tag-namespace-name",name])}'],
                     profile, region)
    defaults = read(['iam', 'tag-default', 'list', '--compartment-id', scope, '--limit', LIMIT,
                     '--query', 'data[].{name:"tag-definition-name",required:"is-required"}'],
                    profile, region)
    budgets = read(['budgets', 'budget', 'budget', 'list', '--compartment-id', root,
                    '--limit', LIMIT, '--query', 'data[].{name:"display-name"}'], profile, region)
    quotas = read(['limits', 'quota', 'list', '--compartment-id', root, '--limit', LIMIT,
                   '--query', 'data[].{name:name}'], profile, region)

    reads = {'compartments': compartments, 'tag_namespaces': namespaces,
             'cost_tracking_tags': cost_tags, 'tag_defaults': defaults,
             'budgets': budgets, 'quotas': quotas}
    unreadable = sorted(k for k, v in reads.items() if v is None)
    counts = {k: len(v) for k, v in reads.items() if v is not None}
    findings = []
    if compartments is not None and not compartments:
        findings.append('everything_lives_in_root_compartment')
    if quotas is not None and not quotas:
        findings.append('no_compartment_quota_blocks_spend')
    if budgets is not None and not budgets:
        findings.append('no_budget_alert_configured')
    if cost_tags is not None and names(cost_tags, 'name') == ['Oracle-Tags.CreatedBy']:
        findings.append('only_the_default_cost_tracking_tag')
    if defaults is not None and not any(row.get('required') for row in defaults
                                        if isinstance(row, dict)):
        findings.append('no_required_tag_default_in_scope')

    print(emit({'ok': not unreadable, 'scope': 'tenancy_root_plus_one_compartment',
                'complete': False, 'bounded_at': int(LIMIT), 'counts': counts,
                'cost_tracking_tags': names(cost_tags or [], 'name'),
                'tag_namespaces': names(namespaces or [], 'name'),
                'unreadable': unreadable, 'findings': findings, 'mutated': False}))
    return 0 if not unreadable else 1


if __name__ == '__main__':
    raise SystemExit(main())
