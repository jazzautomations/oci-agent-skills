#!/usr/bin/env python3
"""Run and publish V1–V28; failures remain red and never authorize tenancy writes.

Default reuses dated live/public-link evidence. --live repeats only D7 reads;
--links repeats public documentation GETs. No hosted workflows or agents launch.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PYTHON = [sys.executable]
DATE = datetime.now(timezone.utc).date().isoformat()


def execute(identifier, command, display, *, timeout=240, owner='repository maintainers', note=''):
    try:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        ok = result.returncode == 0
        detail = note or ('Command passed.' if ok else 'Command failed; inspect local output by rerunning the command.')
        if identifier == 'V19':
            report = json.loads((ROOT/'evals/results/offline.json').read_text())
            detail = f"Description proxy {report['metrics']['routing_accuracy']:.1%}; required ≥90%; overlap pairs {report['metrics']['overlap_pairs_correct']}/4. Not host routing."
        elif identifier == 'V14':
            import re
            summary = re.search(r'(\d+ passed[^\n]*)', result.stdout)
            if summary: detail = summary[1]
        return {'id':identifier, 'command':display, 'result':'PASS' if ok else 'FAIL', 'date':DATE,
                'exit_code':result.returncode, 'detail':detail, 'owner':None if ok else owner}
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return {'id':identifier,'command':display,'result':'FAIL','date':DATE,'detail':'Unavailable command, timeout or invalid report; raw output suppressed.','owner':owner}


def archived(identifier, path, command, key, *, owner):
    try:
        data=json.loads(path.read_text())
        ok=bool(data[key])
        return {'id':identifier,'command':command,'result':'PASS' if ok else 'FAIL',
                'date':data.get('validated_at', data.get('date', 'unrecorded'))[:10], 'detail':'Recorded evidence from this handoff; see '+str(path.relative_to(ROOT))+'.', 'owner':None if ok else owner}
    except (OSError,ValueError,KeyError):
        return {'id':identifier,'command':command,'result':'UNMEASURED','date':DATE,'detail':'No valid recorded evidence.','owner':owner}


def distribution():
    with tempfile.TemporaryDirectory(prefix='oci-release-copy-') as directory:
        target=Path(directory)/'plugin'
        command=['bash','installers/install.sh','--target',str(target),'--host','claude','--copy-shared']
        subprocess.run(command,cwd=ROOT,check=True,capture_output=True)
        links=subprocess.check_output(['find','.', '-type','l'],cwd=target,text=True)
        assert not links.strip()
        assert len(list((target/'skills').glob('*/SKILL.md'))) == 33
        assert all((target/p).is_file() for p in ('hooks/hooks.json','.mcp.json','NOTICE','LICENSE'))
        assert not list(target.rglob('.handoff-*'))
        assert not (target/'research').exists()
    return 'Fresh copied tree: 33 skills, shared refs, hooks, MCP config and notices; find . -type l empty.'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cli-python',type=Path)
    parser.add_argument('--live',action='store_true')
    parser.add_argument('--links',action='store_true')
    parser.add_argument('--live-help',action='store_true')
    parser.add_argument('--distribution-only',action='store_true')
    args=parser.parse_args()
    if args.distribution_only:
        print(distribution());return 0
    executable=shutil.which('oci')
    cli_python=args.cli_python or (Path(executable).resolve().parent/'python' if executable else Path(sys.executable))
    specs=[]
    def add(i,argv,display=None,**kwargs):
        specs.append((i,argv,display or shlex.join(argv),kwargs))
    def check(i,name,*extra,**kwargs):
        add(i,PYTHON+['scripts/ci/'+name+'.py',*extra], 'uv run --frozen --project runtime python scripts/ci/'+name+'.py'+(' '+shlex.join(extra) if extra else ''),**kwargs)
    def test(i,*extra,**kwargs):
        add(i,PYTHON+['-m','pytest','-q',*extra], 'uv run --frozen --project runtime pytest -q '+shlex.join(extra),**kwargs)
    add('V1',['claude','plugin','validate','.','--strict'])
    add('V2',['claude','plugin','validate','./skills','--strict'])
    check('V3','check_frontmatter'); check('V4','check_portable'); check('V5','check_refs')
    check('V6','lint_fences','skills','docs','README.md', *(['--live-help'] if args.live_help else []),timeout=1200)
    test('V8','tests/test_guard.py',note='Measured current matrix is stricter than the original plan: destructive 1/997/328, not 2/996/328; non-OCI rules remain unmeasured.')
    test('V9','tests','-k','parse')
    test('V10','tests','-k','plugin_script')
    check('V11','check_scripts_readonly')
    test('V12','tests','-k','redact or sanitize')
    add('V13',['uv','run','--frozen','--project','runtime','oci-readonly-smoke'])
    test('V14','tests','skills/oci-incident-triage/tests','skills/oci-security-posture/tests','skills/oci-sdk-patterns/tests')
    test('V15','tests/test_packaging.py','tests/test_installer.py',timeout=360)
    test('V16','tests/test_catalog.py')
    test('V17','tests/test_console_url.py')
    add('V18',[str(cli_python),'scripts/check_examples.py','--report','docs/validation-examples-offline.json'],'CLI_PYTHON scripts/check_examples.py --report docs/validation-examples-offline.json')
    add('V19',PYTHON+['scripts/eval/run.py','--json','evals/results/offline.json'],'uv run --frozen --project runtime python scripts/eval/run.py --json evals/results/offline.json',owner='evaluation/routing maintainers')
    add('V20',PYTHON+['evals/run_routing.py','--negatives'],'uv run --frozen --project runtime python evals/run_routing.py --negatives',note='Zero negative firings required; the matcher is a static proxy.')
    check('V21','check_budget');check('V22','check_no_secrets');check('V23','check_licenses')
    # Additional integrity subchecks attach to their parent gate, not new V numbers.
    add('V16-regeneration',[str(cli_python),'scripts/inventory.py','--format','jsonl','--index','--check'],'CLI_PYTHON scripts/inventory.py --format jsonl --index --check')
    check('V22-history','check_history')
    add('V28-offline',PYTHON+['scripts/eval/head_to_head.py'],'uv run --frozen --project runtime python scripts/eval/head_to_head.py')
    add('V24-local',[str(cli_python),'scripts/ci/cli_drift.py'],'CLI_PYTHON scripts/ci/cli_drift.py')
    rows=[]
    # Independent read-only validations; no mutation tests are executed against OCI.
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures={pool.submit(execute,i,cmd,display,**kwargs):i for i,cmd,display,kwargs in specs}
        for future in as_completed(futures):
            row=future.result();rows.append(row)
            print(row['id']+': '+row['result'],flush=True)
    if args.links:
        command=PYTHON+['scripts/ci/check_links.py']
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=600)
        # Checker returns fixed public URLs/statuses only.
        data=json.loads(result.stdout)
        data['validated_at']=datetime.now(timezone.utc).isoformat()
        (ROOT/'docs/validation-links.json').write_text(json.dumps(data,indent=2)+'\n')
    rows.append(archived('V7',ROOT/'docs/validation-links.json','uv run --frozen --project runtime python scripts/ci/check_links.py','ok',owner='documentation maintainers / public documentation host'))
    if args.live:
        row=execute('V25',[str(cli_python),'scripts/check_examples.py','--live','--profile','DEFAULT','--region','us-chicago-1','--report','docs/validation-cli.json'],
                    'CLI_PYTHON scripts/check_examples.py --live --profile DEFAULT --region us-chicago-1 --report docs/validation-cli.json',timeout=600,owner='OCI operator / CLI validation maintainers')
        rows.append(row)
        environment=dict(os.environ,OCI_CONFIG_PROFILE='DEFAULT',OCI_CLI_PROFILE='DEFAULT')
        result=subprocess.run(['uv','run','--frozen','--project','runtime','oci-readonly-smoke','--live','--region','us-chicago-1'],cwd=ROOT,env=environment,capture_output=True,text=True,timeout=240)
        data=json.loads(result.stdout)
        data['validated_at']=datetime.now(timezone.utc).isoformat()
        (ROOT/'docs/validation-mcp.json').write_text(json.dumps(data,indent=2)+'\n')
    else:
        rows.append(archived('V25',ROOT/'docs/validation-cli.json','CLI_PYTHON scripts/check_examples.py --live --profile DEFAULT --region us-chicago-1 --report docs/validation-cli.json','complete',owner='OCI operator / CLI validation maintainers'))
    rows.append(archived('V26',ROOT/'docs/validation-mcp.json','OCI_CONFIG_PROFILE=DEFAULT OCI_CLI_PROFILE=DEFAULT uv run --frozen --project runtime oci-readonly-smoke --live --region us-chicago-1','ok',owner='OCI operator / MCP maintainers'))
    # No hosted issue creation or agent execution is authorized by this harness.
    rows.extend([
        {'id':'V24','command':'CLI_PYTHON scripts/ci/cli_drift.py; .github/workflows/cli-drift.yml', 'result':'PARTIAL','date':DATE,'detail':'Local pinned required-flag renderer exercised; Tuesday schedule/hosted issue creation not executed locally.','owner':'repository CI maintainers'},
        {'id':'V27','command':'claude plugin eval . --threshold 0.8 --json evals/results/run.json','result':'UNAVAILABLE','date':json.loads((ROOT/'evals/results/host.json').read_text())['date'],'detail':'Prior handoff attempt returned early-access unavailable (evals/results/host.json). Both task shapes supplied; no model-backed skill-creator score measured. Offline proxy cannot establish ≥0.8.','owner':'Claude early-access provider / evaluation maintainers'},
        {'id':'V28','command':'uv run --frozen --project runtime python scripts/eval/head_to_head.py','result':'PARTIAL','date':DATE,'detail':'All four offline arms complete, table and per-case retrieval deltas published. Original live/model-backed comparison and behavioral deltas unmeasured.','owner':'evaluation maintainers'},
    ])
    extras={r['id']:r for r in rows if '-' in r['id']}
    rows=[r for r in rows if '-' not in r['id']]
    for parent,sub in [('V16','V16-regeneration'),('V22','V22-history'),('V24','V24-local'),('V28','V28-offline')]:
        row=next(r for r in rows if r['id']==parent);part=extras[sub]
        row['command']+='; '+part['command']
        if part['result']=='FAIL': row.update(result='FAIL',owner=part['owner'])
        row['detail']+=' Subcheck '+sub+': '+part['result']+'.'
    try:
        detail=distribution()
        next(r for r in rows if r['id']=='V15')['detail']+=' '+detail
    except (OSError,AssertionError,subprocess.SubprocessError):
        next(r for r in rows if r['id']=='V15').update(result='FAIL',detail='Distributed copy failed validation.',owner='packaging maintainers')
    rows.sort(key=lambda r:int(r['id'][1:]))
    assert len(rows)==28
    report={'date':DATE,'branch':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
            'ready':all(r['result']=='PASS' for r in rows),'rows':rows,'subchecks':list(extras.values())}
    (ROOT/'docs/validation-matrix.json').write_text(json.dumps(report,indent=2)+'\n')
    text='# Final validation matrix — '+DATE+'\n\nBranch: v2-foundation. **Not release-ready.** No merge and no tenancy mutations.\n\n'
    text+='Reproduce: `uv run --frozen --project runtime python scripts/ci/release_gate.py --live --links --live-help`. This repeats only bounded D7 reads and public documentation GETs. Omit these flags to reuse dated live/link evidence and use snapshot fence lint. CLI_PYTHON denotes Python from the pinned OCI CLI installation; pass --cli-python to select it explicitly. A nonzero exit is expected while any gate remains red or unmeasured.\n\n'
    text+='| Gate | Command | Result | Date | Evidence / reason / owner |\n|---|---|---|---|---|\n'
    for row in rows:
        detail=row['detail']+(' Owner: '+row['owner']+'.' if row.get('owner') else '')
        text+='| '+row['id']+' | `'+row['command'].replace('|','\\|')+'` | '+row['result']+' | '+row['date']+' | '+detail.replace('|','\\|')+' |\n'
    text+='\nPASS refers to the stated scope. V8 is the current measured OCI-leaf matrix; it does not measure non-OCI rules. V19/V20 are deterministic description proxies. V24 is not a hosted schedule run. V27 and the original behavioral V28 remain unmeasured. V25/V26 verify bounded selected reads, not deployed workloads or complete inventories. The distributed tree is checked before any uv-created environment symlinks.\n'
    (ROOT/'docs/validation-matrix.md').write_text(text)
    print(json.dumps({'ready':report['ready'],'nonpassing':[r['id'] for r in rows if r['result']!='PASS']},indent=2))
    return int(not report['ready'])


if __name__=='__main__':raise SystemExit(main())
