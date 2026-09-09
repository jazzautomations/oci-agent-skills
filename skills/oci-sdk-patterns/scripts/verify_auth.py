#!/usr/bin/env python3
"""Check an explicitly selected CLI auth mode with two wrapper-protected reads.

This verifies the selected CLI signer, not execution of any SDK recipe. JSON output is
unconditional. No key, token or OCID is printed; principal modes need TENANCY_ID.
"""
import argparse
import json
import os
import sys
from pathlib import Path


def plugin_root():
    root = os.environ.get('CLAUDE_PLUGIN_ROOT')
    if root:
        return Path(root)
    for parent in Path(__file__).resolve().parents:
        if (parent / 'scripts' / 'lib' / 'oci_ro.py').is_file():
            return parent
    raise SystemExit('cannot locate the plugin root')


sys.path.insert(0, str(plugin_root() / 'scripts'))
from lib.oci_ro import run  # noqa: E402  (path is resolved above)

# Keys read from the profile section. Values are never printed, only their presence.
SESSION = 'security_token_file'
DELEGATION = 'delegation_token_file'


def section(config, profile):
    """Read one profile section offline. Returns {key: value} for the keys we care about."""
    wanted = {'user', 'tenancy', 'region', 'key_file', 'key_content', SESSION, DELEGATION}
    found, inside = {}, False
    try:
        lines = Path(config).expanduser().read_text().splitlines()
    except OSError:
        return None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('['):
            inside = stripped == f'[{profile}]'
            continue
        if not inside or '=' not in stripped or stripped.startswith('#'):
            continue
        key, _, value = stripped.partition('=')
        key = key.strip()
        if key in wanted:
            found[key] = value.strip()
    return found


AUTH = {
    'api_key': 'config + API-key signer',
    'security_token': 'SecurityTokenSigner',
    'instance_principal': 'InstancePrincipalsSecurityTokenSigner',
    'instance_obo_user': 'InstancePrincipalsDelegationTokenSigner',
    'resource_principal': 'get_resource_principals_signer',
    'oke_workload_identity': 'get_oke_workload_identity_resource_principal_signer',
}


def probe(argv, args, region):
    result = run([*argv, '--auth', args.auth, '--config-file', str(Path(args.config).expanduser())],
                 profile=args.profile, region=region)
    return {'ok': result['ok'], 'detail': None if result['ok'] else result['error'].get('kind')}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--profile', default=os.environ.get('OCI_CLI_PROFILE'))
    parser.add_argument('--region', default=os.environ.get('OCI_CLI_REGION'))
    parser.add_argument('--config', default=os.environ.get('OCI_CLI_CONFIG_FILE', '~/.oci/config'))
    parser.add_argument('--auth', choices=AUTH, default=os.environ.get('OCI_CLI_AUTH', 'api_key'))
    parser.add_argument('--json', action='store_true', help='Emit JSON (default)')
    args = parser.parse_args()
    if not args.profile:
        parser.error('Set --profile or OCI_CLI_PROFILE explicitly')

    keys = section(args.config, args.profile)
    resolved, how = args.auth, AUTH[args.auth]
    if resolved in ('api_key', 'security_token', 'instance_obo_user') and not keys:
        parser.error('Selected config/profile is missing or empty')
    region = args.region or (keys or {}).get('region')
    tenancy = os.environ.get('TENANCY_ID') or (keys or {}).get('tenancy')
    if not region or not tenancy:
        parser.error('Set region and TENANCY_ID (or profile tenancy) explicitly')

    checks = {'list_regions': probe(['iam', 'region', 'list', '--query', 'length(data)'],
                                   args, region)}
    if tenancy:
        checks['get_compartment_tenancy'] = probe(
            ['iam', 'compartment', 'get', '--compartment-id', tenancy,
             '--query', 'data."lifecycle-state"'], args, region)
    else:
        checks['get_compartment_tenancy'] = {'ok': False, 'detail': 'no tenancy in profile'}

    print(json.dumps({
        'profile': args.profile,
        'config': args.config,
        'auth_mode': resolved,
        'signer': how,
        'region': region,
        'tenancy_known': bool(tenancy),
        'checks': checks,
        'note': 'The selected CLI auth/config completed these reads; SDK recipes were not executed.',
    }, indent=2, sort_keys=True))
    return 0 if all(c['ok'] for c in checks.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
