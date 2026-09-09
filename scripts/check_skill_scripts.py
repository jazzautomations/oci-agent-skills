#!/usr/bin/env python3
"""Execute skill entrypoints with fixed scope; retain only status, never captured output.

SQL files are inert examples and are recorded without execution. Missing resource
prerequisites remain blocked; this runner never creates them or substitutes fake IDs.
"""
import argparse
import configparser
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def outcome(returncode, stdout, stderr):
    objects = []
    decoder = json.JSONDecoder()
    rest = stdout.lstrip()
    while rest:
        try:
            value, end = decoder.raw_decode(rest)
        except ValueError:
            break
        objects.append(value)
        rest = rest[end:].lstrip()
    def failed(value):
        if isinstance(value, dict):
            return value.get('ok') is False or bool(value.get('error')) or any(failed(v) for v in value.values())
        return isinstance(value, list) and any(failed(v) for v in value)
    if returncode == 0 and not any(failed(v) for v in objects):
        return 'passed'
    if 'required' in stderr.lower() or 'set ' in stderr.lower() or 'unbound variable' in stderr:
        return 'blocked_missing_prerequisite'
    return 'failed'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', required=True)
    parser.add_argument('--profile', required=True)
    parser.add_argument('--region', required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    try:
        config = configparser.ConfigParser(interpolation=None)
        config.read(Path(os.getenv('OCI_CLI_CONFIG_FILE', '~/.oci/config')).expanduser())
        section = config[args.profile]
        tenancy = section['tenancy']
        if section.get('endpoint'):
            raise ValueError('Endpoint override')
        environment = {k:v for k,v in os.environ.items() if not k.endswith('_ID') and k not in {'OCI_RO_TRACE','OCI_RO_ALLOW_ALL','OCI_CLI_ENDPOINT','OCI_ENDPOINT','AD','LIMIT_NAME','SHAPE','MQL','BUCKET','NAMESPACE','POLICY_ID','INSTANCE_ID'}}
        environment.update(PROFILE=args.profile, REGION=args.region, TENANCY_ID=tenancy,
            COMPARTMENT_ID=tenancy, OCI_CLI_PROFILE=args.profile, OCI_CLI_REGION=args.region,
            OCI_RO_SMOKE_SCOPE=tenancy, OCI_RO_SMOKE_PROFILE=args.profile, OCI_RO_SMOKE_REGION=args.region,
            CLAUDE_PLUGIN_ROOT=str(ROOT), SHAPE='VM.Standard.A1.Flex', SERVICE='compute')
        # Explicit bounded time windows; never request historical account dumps.
        end = datetime.now(timezone.utc).date()
        moment = datetime.now(timezone.utc)
        environment.update(START_TIME=(moment-timedelta(hours=1)).isoformat(), END_TIME=moment.isoformat(),
                           METRIC_NAMESPACE='oci_computeagent', MQL='CpuUtilization[5m].mean()')
        environment.update(PRIOR_START=str(end-timedelta(days=2)), PRIOR_END=str(end-timedelta(days=1)),
                           CURRENT_START=str(end-timedelta(days=1)), CURRENT_END=str(end), WINDOW_HOURS='1')
    except (KeyError, ValueError, OSError):
        print(json.dumps({'ok':False,'error':'local_scope_configuration'}))
        return 1
    # Discover only prerequisite metadata in the same selected compartment; failures
    # never cause a broader search or a retry in another scope.
    from lib.oci_ro import run_process
    discovery = [
        ('AD', ['iam','availability-domain','list','--compartment-id',tenancy,'--query','data[0].name']),
        ('LIMIT_NAME', ['limits','definition','list','--compartment-id',tenancy,'--service-name','compute','--limit','1','--query','data[0].name']),
        ('INSTANCE_ID', ['compute','instance','list','--compartment-id',tenancy,'--limit','1','--query','data[0].id']),
    ]
    bootstrap = []
    for name, argv in discovery:
        try:
            response = run_process([*argv,'--profile',args.profile,'--region',args.region,'--no-retry'],
                                   capture_output=True,text=True,timeout=30)
            value = json.loads(response.stdout) if response.returncode == 0 and response.stdout.strip() else None
            if isinstance(value, str) and value:
                environment[name] = value
            bootstrap.append({'field':name,'resolved':name in environment})
        except (OSError, ValueError, subprocess.TimeoutExpired):
            bootstrap.append({'field':name,'resolved':False})
    rows = []
    with tempfile.TemporaryDirectory(prefix='oci-skill-smoke-') as directory:
        empty = Path(directory)/'empty.json'; empty.write_text('[]')
        plan = Path(directory)/'plan.json'; plan.write_text('{"format_version":"1.2","resource_changes":[]}')
        tails = {'chat_min.py':['--api-format','GENERIC'], 'merge_rules.py':[str(empty),str(empty)],
                 'plan_summary.py':[str(plan)], 'fetch_spec.py':['identity','--url'],
                 'price.sh':['B88514','USD'], 'list_all.sh':['os ns get','--profile',args.profile,'--region',args.region,'--query','data'],
                 'whoami.sh':['--profile',args.profile,'--region',args.region],
                 'verify_auth.py':['--profile',args.profile,'--region',args.region,'--auth','api_key']}
        for path in sorted((ROOT/'skills').glob('*/scripts/*')):
            if not path.is_file():
                continue
            row = {'script':path.relative_to(ROOT).as_posix()}
            if path.suffix not in {'.py','.sh'}:
                row.update(status='inert_not_executed', reason='Non-executable example; no database session or mutation fixture is run.')
            else:
                command = [sys.executable if path.suffix == '.py' else 'bash',str(path),*tails.get(path.name,[])]
                try:
                    result = subprocess.run(command,cwd=ROOT,env=environment,capture_output=True,text=True,timeout=120)
                    row.update(status=outcome(result.returncode,result.stdout,result.stderr),exit_code=result.returncode)
                    if path.name == 'whoami.sh' and row['status'] == 'passed':
                        identity = json.loads(result.stdout)
                        if any(identity.get(k) is None for k in ('identity','subscriptions','compartments')):
                            row['status'] = 'failed_incomplete_identity'
                except subprocess.TimeoutExpired:
                    row.update(status='timeout')
                except OSError:
                    row.update(status='launch_failed')
                if row['status'] != 'passed':
                    row['owner'] = 'OCI operator / skill maintainer'
            rows.append(row)
            print(json.dumps(row),flush=True)
    report = {'validated_at':datetime.now(timezone.utc).isoformat(), 'mode':'scoped_script_execution',
              'scope':'Selected profile tenancy compartment and region; one bounded page per call. Captured stdout/stderr discarded.',
              'bootstrap':bootstrap, 'complete':all(r['status'] in {'passed','inert_not_executed'} for r in rows), 'checks':rows}
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2)+'\n')
    return int(not report['complete'])


if __name__ == '__main__':
    raise SystemExit(main())
