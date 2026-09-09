#!/usr/bin/env python3
'''Lint IAM policy statements offline, or lint the statements a live policy already has.'''
import argparse
import json
import os
import re
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from lib.oci_ro import run
from lib.sanitize import emit

FAMILIES = json.loads((ROOT / 'references' / 'resource-type-families.json').read_text())['families']
START = ('allow', 'endorse', 'admit', 'define')
VERBS = ('inspect', 'read', 'use', 'manage')
BROAD = {'any-user': 'any-user grants users, resource, instance and service principals; prefer any-group',
         'all-resources': 'all-resources widens with every new service; name individual resource-types',
         'in tenancy': 'attached at the tenancy: only tenancy policy-admins can edit it'}


def statement(text):
    '''Return the findings for one statement; empty list means nothing to report.'''
    found = []
    lowered = ' '.join(text.lower().split())
    if lowered.startswith('deny'):
        return ['there is no Deny in IAM policy: absence of an Allow is the deny']
    if lowered.split(' ')[0] in ('set', 'zero', 'unset'):
        return ['quota statement, not IAM policy: lint it with oci-tenancy-governance']
    if not lowered.startswith(START):
        return ['does not start with Allow, Endorse, Admit or Define']
    if lowered.startswith('allow'):
        if ' in ' not in lowered:
            found.append('no location: add "in tenancy" or "in compartment <name>"')
        if sum(lowered.count(' %s ' % verb) for verb in VERBS) != 1:
            found.append('a statement takes exactly one verb')
        for family, members in FAMILIES.items():
            if family in lowered:
                found.append('%s expands to %d individual resource-types and widens silently' % (family, len(members)))
    for token, why in BROAD.items():
        if token in lowered:
            found.append(why)
    if '!=' in lowered and 'request.permission' in lowered:
        found.append('request.permission != is a denylist: it auto-grants future permissions')
    if re.search(r'where\s+(any|all)\s*\{[^}]*$', lowered):
        found.append('unclosed any{ } / all{ } condition block')
    if lowered.count("'") % 2:
        found.append('odd number of single quotes')
    if 'request.region' in lowered and re.search(r"request\.region\s*=\s*'[a-z]{2}-[a-z]+-\d'", lowered):
        found.append('request.region takes the 3-letter key (ORD), not the region name')
    return found


def statements(args):
    if args.policy_id:
        result = run(['iam', 'policy', 'get', '--policy-id', args.policy_id,
                      '--query', 'data.statements'],
                     profile=os.environ['OCI_CLI_PROFILE'], region=os.environ['OCI_CLI_REGION'])
        if not result['ok']:
            raise ValueError('policy read failed')
        data = result['data']
        return data['items'] if isinstance(data, dict) and 'items' in data else data
    text = sys.stdin.read() if args.file == '-' else Path(args.file).read_text()
    return json.loads(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__, epilog='Live --policy-id requires OCI_CLI_PROFILE and OCI_CLI_REGION. JSON output is unconditional.')
    parser.add_argument('--json', action='store_true', help='Emit JSON (default)')
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--file', help='JSON array of statements, or - for stdin')
    source.add_argument('--policy-id', help='OCID of a policy to read read-only and lint')
    args = parser.parse_args()
    if args.policy_id and not all(os.environ.get(k) for k in ('OCI_CLI_PROFILE', 'OCI_CLI_REGION')):
        parser.error('Set OCI_CLI_PROFILE and OCI_CLI_REGION for live reads')
    try:
        rows = statements(args)
        if not isinstance(rows, list) or not all(isinstance(r, str) for r in rows):
            raise ValueError('expected a JSON array of statement strings')
    except (ValueError, OSError, json.JSONDecodeError):
        print(emit({'ok': False, 'kind': 'unreadable_statements'}))
        return 2
    findings = [{'index': i, 'findings': f} for i, r in enumerate(rows) if (f := statement(r))]
    print(emit({'ok': True, 'statements': len(rows), 'flagged': len(findings), 'items': findings,
                'note': 'advisory syntax and blast-radius review; IAM is the boundary'}))
    return 1 if findings else 0


if __name__ == '__main__':
    raise SystemExit(main())
