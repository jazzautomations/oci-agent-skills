#!/usr/bin/env python3
'''Bounded read-only posture sweep: severity, resource, evidence command, proposed fix.'''
import argparse
import hashlib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts'))
from lib.oci_ro import run
from lib.sanitize import emit

MAX_USERS = 25
MAX_BUCKETS = 25
RISKY_PORTS = {22, 3389}


def read(argv, flags):
    '''One bounded read, cleaned and redacted. Returns the projection, or None on failure.'''
    result = run(argv, profile=os.environ['PROFILE'], region=os.environ['REGION'])
    if not result['ok']:
        return None
    for flag in result['data'].get('flags', []):
        if flag not in flags:
            flags.append(flag)
    return result['data'].get('items')


def age_days(stamp):
    try:
        moment = datetime.fromisoformat(str(stamp).replace('Z', '+00:00'))
    except ValueError:
        return None
    return (datetime.now(timezone.utc) - moment).days if moment.tzinfo else None


def finding(check, severity, resource, evidence, fix):
    reference = 'sha256:' + hashlib.sha256(str(resource).encode()).hexdigest()[:12]
    return {'check': check, 'severity': severity, 'resource': reference,
            'evidence': evidence, 'fix': fix}


def identity(tenancy, findings, unread, flags):
    listed = read(['iam', 'user', 'list', '--compartment-id', tenancy, '--limit', str(MAX_USERS),
                   '--query', 'data[].{n:name,mfa:"is-mfa-activated"}'], flags)
    if not isinstance(listed, list):
        return unread.append('iam user list')
    if len(listed) == MAX_USERS:
        unread.append('users beyond the first %d' % MAX_USERS)
    for user in listed:
        if user.get('mfa') is False:
            findings.append(finding('user-without-mfa', 'HIGH', user.get('n'),
                                    'oci iam user list --compartment-id <tenancy> --limit 25',
                                    'enable MFA for this user in the identity domain'))


def key_age(findings, unread, flags):
    '''Key age needs a user OCID; the wrapper redacts OCIDs, so the operator supplies one.'''
    user = os.environ.get('USER_ID')
    if not user:
        return unread.append('api-key age (set USER_ID to check one user)')
    keys = read(['iam', 'user', 'api-key', 'list', '--user-id', user,
                 '--query', 'data[].{c:"time-created"}'], flags)
    if not isinstance(keys, list):
        return unread.append('iam user api-key list')
    for key in keys:
        days = age_days(key.get('c'))
        if days is not None and days > int(os.environ.get('MAX_KEY_AGE_DAYS', '90')):
            findings.append(finding('stale-api-key', 'MEDIUM', 'key %s days old' % days,
                                    'oci iam user api-key list --user-id <user>',
                                    'user uploads a new key, then delete the old fingerprint'))


def policies(compartment, findings, unread, flags):
    listed = read(['iam', 'policy', 'list', '--compartment-id', compartment, '--limit', '100',
                   '--query', 'data[].{n:name,s:statements}'], flags)
    if not isinstance(listed, list):
        return unread.append('iam policy list')
    for policy in listed:
        for statement in policy.get('s') or []:
            lowered = str(statement).lower()
            if 'any-user' in lowered or 'manage all-resources' in lowered:
                findings.append(finding('over-broad-policy', 'HIGH', policy.get('n'),
                                        'oci iam policy list --compartment-id <compartment> --limit 100',
                                        'narrow the subject and resource-type; see oci-iam-policy'))


def buckets(compartment, findings, unread, flags):
    space = read(['os', 'ns', 'get', '--query', 'data'], flags)
    namespace = os.environ.get('NAMESPACE') or (space if isinstance(space, str) else None)
    if not namespace:
        return unread.append('os ns get')
    names = read(['os', 'bucket', 'list', '--compartment-id', compartment,
                  '--namespace-name', namespace, '--limit', str(MAX_BUCKETS),
                  '--query', 'data[].name'], flags)
    if not isinstance(names, list):
        return unread.append('os bucket list')
    for name in names[:MAX_BUCKETS]:
        row = read(['os', 'bucket', 'get', '--namespace-name', namespace, '--bucket-name', str(name),
                    '--query', 'data.{p:"public-access-type",k:"kms-key-id"}'], flags)
        if not isinstance(row, dict):
            unread.append('os bucket get for one bucket')
            continue
        if row.get('p') not in (None, 'NoPublicAccess'):
            findings.append(finding('public-bucket', 'CRITICAL', name,
                                    'oci os bucket get --namespace-name <ns> --bucket-name <name>',
                                    'set public-access-type NoPublicAccess; audit what was exposed'))
        if not row.get('k'):
            findings.append(finding('bucket-without-cmk', 'MEDIUM', name,
                                    'oci os bucket get --namespace-name <ns> --bucket-name <name>',
                                    'assign a Vault key if policy requires customer-managed keys'))


def ingress(compartment, findings, unread, flags):
    listed = read(['network', 'security-list', 'list', '--compartment-id', compartment, '--limit', '100',
                   '--query', 'data[].{n:"display-name",r:"ingress-security-rules"}'], flags)
    if not isinstance(listed, list):
        return unread.append('network security-list list')
    for entry in listed:
        for rule in entry.get('r') or []:
            if not isinstance(rule, dict) or rule.get('source') not in ('0.0.0.0/0', '::/0'):
                continue
            options = rule.get('tcp-options') or {}
            ports = options.get('destination-port-range') or {}
            port = ports.get('min')
            upper = ports.get('max', port)
            protocol = str(rule.get('protocol'))
            tcp_open = protocol in ('6', 'all') and (port is None or any(port <= p <= upper for p in RISKY_PORTS))
            severe = 'CRITICAL' if tcp_open else 'HIGH'
            where = 'port %s' % port if port is not None else 'protocol %s, all ports' % rule.get('protocol')
            findings.append(finding('open-ingress', severe, '%s %s' % (entry.get('n'), where),
                                    'oci network security-list list --compartment-id <compartment> --limit 100',
                                    'replace 0.0.0.0/0 with the caller CIDR, or move the port behind a bastion'))


def main():
    parser = argparse.ArgumentParser(description=__doc__, epilog='Required env: PROFILE REGION COMPARTMENT_ID TENANCY_ID. Optional USER_ID, NAMESPACE, MAX_KEY_AGE_DAYS (positive integer, default 90). Resource labels are SHA-256 pseudonyms; JSON output is unconditional.')
    parser.add_argument('--json', action='store_true', help='Emit JSON (default)')
    parser.parse_args()
    required = ('PROFILE', 'REGION', 'COMPARTMENT_ID', 'TENANCY_ID')
    if not all(os.environ.get(key) for key in required):
        parser.error('Set ' + ', '.join(required) + '; optional USER_ID, NAMESPACE, MAX_KEY_AGE_DAYS (default 90)')
    try:
        if int(os.environ.get('MAX_KEY_AGE_DAYS', '90')) <= 0:
            raise ValueError
    except ValueError:
        parser.error('MAX_KEY_AGE_DAYS must be a positive integer')
    compartment, tenancy = os.environ['COMPARTMENT_ID'], os.environ['TENANCY_ID']
    findings, unread, flags = [], [], []
    identity(tenancy, findings, unread, flags)
    key_age(findings, unread, flags)
    policies(compartment, findings, unread, flags)
    buckets(compartment, findings, unread, flags)
    ingress(compartment, findings, unread, flags)
    order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2}
    findings.sort(key=lambda row: order.get(row['severity'], 3))
    print(emit({'ok': not unread, 'region': os.environ['REGION'], 'findings': findings,
                'unread': unread, 'untrusted_flags': flags, 'created': False,
                'complete': False, 'note': 'One compartment, capped pages. Absence is not compliance.'}))
    return 0 if not unread else 1


if __name__ == '__main__':
    raise SystemExit(main())
