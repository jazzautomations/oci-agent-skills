#!/usr/bin/env python3
"""Run and publish V1–V28; failures remain red and never authorize tenancy writes.

Default reuses dated live/public-link evidence; outputs go to scratch and are diffed. --live repeats only D7 reads;
--links repeats public documentation GETs. The host eval probe grants no execution tools and disables publication.
"""
import argparse
import difflib
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
            report = json.loads(Path(command[-1]).read_text())
            accuracy = report['metrics']['routing_accuracy']
            formatted = f'{accuracy:.1%}' if accuracy is not None else 'unavailable'
            detail = f"Recorded semantic selection, worst trial {formatted}; required ≥90%; overlap pairs {report['metrics']['overlap_pairs_correct']}/4. Input-bound evidence, no fresh CI inference or host task execution."
        elif identifier == 'V22-history':
            counts = json.loads(result.stdout)['counts']
            detail = 'History scan counts: ' + json.dumps(counts, sort_keys=True) + '.'
            owner = 'repository history owner'
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
                'date':data.get('validated_at', data.get('date', 'unrecorded'))[:10], 'detail':'Recorded evidence from this handoff; see '+'/'.join(path.parts[-3:])+'.', 'owner':None if ok else owner}
    except (OSError,ValueError,KeyError):
        return {'id':identifier,'command':command,'result':'UNMEASURED','date':DATE,'detail':'No valid recorded evidence.','owner':owner}


def reference_task_status(audit):
    """A limited fixture score can fail the threshold, never certify full semantics."""
    arm = audit['arms']['native-plugin']
    if arm['attempts'] != 40 or not 0 <= arm['passed'] <= 40:
        raise ValueError('Invalid paired task count')
    return 'FAIL' if arm['passed'] / arm['attempts'] < 0.8 else 'PARTIAL'


def distribution():
    with tempfile.TemporaryDirectory(prefix='oci-release-copy-') as directory:
        target=Path(directory)/'plugin'
        command=['bash','installers/install.sh','--target',str(target),'--host','claude','--copy-shared']
        subprocess.run(command,cwd=ROOT,check=True,capture_output=True)
        links=subprocess.check_output(['find','.', '-type','l'],cwd=target,text=True)
        assert not links.strip()
        assert len(list((target/'skills').glob('*/SKILL.md'))) == len(list((ROOT/'skills').glob('*/SKILL.md')))
        assert all((target/p).is_file() for p in ('hooks/hooks.json','.mcp.json','NOTICE','LICENSE'))
        assert not list(target.rglob('.handoff-*'))
        assert not list(target.rglob('CODEX-STATUS.md'))
        assert not (target/'research').exists()
    return 'Fresh copied tree: all source skills, shared refs, hooks, MCP config and notices; find . -type l empty.'


def diff_evidence(output, root=ROOT):
    """Compare generated artifacts without changing the recorded baseline."""
    changed = []
    for candidate in sorted(p for folder in ('docs','evals/results') for p in (output/folder).rglob('*')):
        if not candidate.is_file():
            continue
        relative = candidate.relative_to(output)
        baseline = root/relative
        before = baseline.read_text() if baseline.is_file() else ''
        after = candidate.read_text()
        if before != after:
            changed.append(relative.as_posix())
            print(''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                fromfile='tracked/'+relative.as_posix(), tofile='scratch/'+relative.as_posix())), end='')
    return changed


def probe_host(output):
    """Probe the installed eval command with no granted execution tools or publication."""
    folder=output/'host-probe'
    folder.mkdir(exist_ok=True)
    command=['claude','plugin','eval','.','--threshold','0.8','--json',str(folder/'run.json'),
             '--output-dir',str(folder),'--no-publish','--no-scaffold','--mocks','record','--max-cost-usd','1','--runs','1']
    environment=dict(os.environ,OCI_CONFIG_FILE=str(folder/'absent'),OCI_CLI_CONFIG_FILE=str(folder/'absent'))
    try:
        result=subprocess.run(command,cwd=ROOT,env=environment,capture_output=True,text=True,timeout=60)
        lines=[line for line in (result.stdout+'\n'+result.stderr).splitlines() if 'early access' in line.lower() or line.startswith(('error:','Error:'))]
        reason='\n'.join(lines)[:1000] or 'No qualifying task score; raw transcript suppressed.'
        status='UNAVAILABLE' if 'early access' in reason else 'UNMEASURED'
        version=subprocess.check_output(['claude','--version'],text=True).strip()
        record={'command':'claude plugin eval . --threshold 0.8 --json SCRATCH/run.json --output-dir SCRATCH --no-publish --no-scaffold --mocks record --max-cost-usd 1 --runs 1',
                'status':status.lower(),'reason':reason,'date':DATE,'host_version':version,'exit_code':result.returncode,
                'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                'scope':'No tool grants, mock MCP, absent OCI config, no scaffold or publication.'}
    except (OSError,subprocess.TimeoutExpired):
        record={'status':'unmeasured','reason':'Host probe unavailable or timed out.','date':DATE}
    (output/'evals/results/host.json').write_text(json.dumps(record,indent=2)+'\n')
    return record


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cli-python',type=Path)
    parser.add_argument('--output-dir',type=Path,help='Scratch directory outside the checkout; tracked evidence is never overwritten')
    parser.add_argument('--live',action='store_true')
    parser.add_argument('--links',action='store_true')
    parser.add_argument('--live-help',action='store_true')
    parser.add_argument('--distribution-only',action='store_true')
    args=parser.parse_args()
    if args.distribution_only:
        print(distribution());return 0
    output = (args.output_dir or Path(tempfile.mkdtemp(prefix='oci-release-evidence-'))).resolve()
    if output == ROOT or output.is_relative_to(ROOT):
        parser.error('--output-dir must be outside the checkout')
    if output.exists() and any(output.iterdir()):
        parser.error('--output-dir must be empty to prevent stale evidence')
    for directory in ('docs/evidence','evals/results'):
        (output/directory).mkdir(parents=True,exist_ok=True)
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
    check('V6','lint_fences','skills','docs','references','README.md', *(['--live-help'] if args.live_help else []),timeout=1200)
    test('V8','tests/test_guard.py',note='Severity matrix: docs/evidence/guard-severity-matrix.json, measured against a sha-pinned snapshot derived from the same generator as the catalog. Independent check: zero allows outside the strict read-only set; after deny rules, classify_leaf returns ask whenever read_only is false. All 278 critical leaves denied. Non-OCI rules are unmeasured.')
    test('V9','tests','-k','parse')
    test('V10','tests','-k','plugin_script')
    check('V11','check_scripts_readonly')
    test('V12','tests','-k','redact or sanitize')
    add('V13',['uv','run','--frozen','--project','runtime','oci-readonly-smoke'])
    test('V14','tests','skills/oci-incident-triage/tests','skills/oci-security-posture/tests','skills/oci-sdk-patterns/tests')
    test('V15','tests/test_packaging.py','tests/test_installer.py',timeout=360)
    test('V16','tests/test_catalog.py')
    test('V17','tests/test_console_url.py')
    add('V18',[str(cli_python),'scripts/check_examples.py','--report',str(output/'docs/evidence/validation-examples-offline.json')],'CLI_PYTHON scripts/check_examples.py --report docs/evidence/validation-examples-offline.json')
    add('V19',PYTHON+['scripts/eval/run.py','--json',str(output/'evals/results/offline.json')],'uv run --frozen --project runtime python scripts/eval/run.py --json evals/results/offline.json',owner='evaluation/routing maintainers')
    add('V20',PYTHON+['evals/run_routing.py','--negatives'],'uv run --frozen --project runtime python evals/run_routing.py --negatives',note='Zero negative firings in every recorded semantic trial; input hashes and predictions are checked offline.')
    check('V21','check_budget');check('V22','check_no_secrets');check('V23','check_licenses')
    # Additional integrity subchecks attach to their parent gate, not new V numbers.
    add('V16-regeneration',[str(cli_python),'scripts/inventory.py','--format','jsonl','--index','--check'],'CLI_PYTHON scripts/inventory.py --format jsonl --index --check')
    add('V16-read-contracts',[str(cli_python),'scripts/generate_read_contracts.py','--check'],'CLI_PYTHON scripts/generate_read_contracts.py --check')
    check('V22-history','check_history')
    add('V28-offline',PYTHON+['scripts/eval/head_to_head.py','--json',str(output/'evals/results/head-to-head.json'),'--markdown',str(output/'docs/head-to-head.md')],'uv run --frozen --project runtime python scripts/eval/head_to_head.py')
    add('V28-fixtures',PYTHON+['scripts/eval/verify_tool_task_benchmark.py','evals/results/tool-task-benchmark-structured-2026-09-11.json'],
        'uv run --frozen --project runtime python scripts/eval/verify_tool_task_benchmark.py evals/results/tool-task-benchmark-structured-2026-09-11.json',
        note='Input-bound verification of 160 normalized synthetic MCP task attempts; retained grades and budget failures. This is not native four-product deployment or universal success.')
    add('V24-local',[str(cli_python),'scripts/ci/cli_drift.py'],'CLI_PYTHON scripts/ci/cli_drift.py')
    add('V27-reference',PYTHON+['scripts/eval/verify_native_reference_benchmark.py','evals/results/native-reference-benchmark-2026-09-11.json'],
        'uv run --frozen --project runtime python scripts/eval/verify_native_reference_benchmark.py evals/results/native-reference-benchmark-2026-09-11.json')
    add('V27-checked',PYTHON+['scripts/eval/verify_checked_task_benchmark.py','evals/results/checked-task-benchmark-2026-09-11.json'],
        'uv run --frozen --project runtime python scripts/eval/verify_checked_task_benchmark.py evals/results/checked-task-benchmark-2026-09-11.json')
    add('V27-checked-syntax',[str(cli_python),'scripts/eval/verify_native_command_audit.py','evals/results/checked-task-benchmark-2026-09-11.json','evals/results/checked-task-command-audit-2026-09-11.json'],
        'CLI_PYTHON scripts/eval/verify_native_command_audit.py evals/results/checked-task-benchmark-2026-09-11.json evals/results/checked-task-command-audit-2026-09-11.json')
    add('V27-syntax',[str(cli_python),'scripts/eval/verify_native_command_audit.py','evals/results/native-reference-benchmark-2026-09-11.json','evals/results/native-reference-command-audit-2026-09-11.json'],
        'CLI_PYTHON scripts/eval/verify_native_command_audit.py evals/results/native-reference-benchmark-2026-09-11.json evals/results/native-reference-command-audit-2026-09-11.json')
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
        (output/'docs/evidence/validation-links.json').write_text(json.dumps(data,indent=2)+'\n')
    rows.append(archived('V7',(output if args.links else ROOT)/'docs/evidence/validation-links.json','uv run --frozen --project runtime python scripts/ci/check_links.py','ok',owner='documentation maintainers / public documentation host'))
    if args.live:
        row=execute('V25',[str(cli_python),'scripts/check_examples.py','--live','--profile','DEFAULT','--region','us-chicago-1','--report',str(output/'docs/evidence/validation-cli.json')],
                    'CLI_PYTHON scripts/check_examples.py --live --profile DEFAULT --region us-chicago-1 --report docs/evidence/validation-cli.json',timeout=600,owner='OCI operator / CLI validation maintainers')
        scripts_row=execute('V25-scripts',PYTHON+['scripts/check_skill_scripts.py','--live','--profile','DEFAULT','--report',str(output/'docs/evidence/validation-scripts.json')], 'python scripts/check_skill_scripts.py --live --profile DEFAULT --report docs/evidence/validation-scripts.json', timeout=1800,owner='OCI operator / skill maintainers')
        row['detail'] += ' Skill entrypoint execution: '+scripts_row['result']+'; see docs/evidence/validation-scripts.json.'
        if scripts_row['result'] != 'PASS': row.update(result='FAIL',owner=scripts_row['owner'])
        rows.append(row)
        environment=dict(os.environ,OCI_CONFIG_PROFILE='DEFAULT',OCI_CLI_PROFILE='DEFAULT')
        result=subprocess.run(['uv','run','--frozen','--project','runtime','oci-readonly-smoke','--live','--region','us-chicago-1'],cwd=ROOT,env=environment,capture_output=True,text=True,timeout=240)
        data=json.loads(result.stdout)
        data['validated_at']=datetime.now(timezone.utc).isoformat()
        (output/'docs/evidence/validation-mcp.json').write_text(json.dumps(data,indent=2)+'\n')
    else:
        row=archived('V25',ROOT/'docs/evidence/validation-cli.json','CLI_PYTHON scripts/check_examples.py --live --profile DEFAULT --region us-chicago-1 --report docs/evidence/validation-cli.json','complete',owner='OCI operator / CLI validation maintainers')
        scripts_row=archived('V25-scripts',ROOT/'docs/evidence/validation-scripts.json','python scripts/check_skill_scripts.py --live --profile DEFAULT --report docs/evidence/validation-scripts.json','complete',owner='OCI operator / skill maintainers')
        row['detail']+=' Skill execution: '+scripts_row['result']+'; see docs/evidence/validation-scripts.json.'
        if scripts_row['result']!='PASS': row.update(result='FAIL',owner=scripts_row['owner'])
        rows.append(row)
    rows.append(archived('V26',(output if args.live else ROOT)/'docs/evidence/validation-mcp.json','OCI_CONFIG_PROFILE=DEFAULT OCI_CLI_PROFILE=DEFAULT uv run --frozen --project runtime oci-readonly-smoke --live --region us-chicago-1','ok',owner='OCI operator / MCP maintainers'))
    host = probe_host(output)
    # Hosted workflow issue creation remains outside the release check.
    rows.extend([
        {'id':'V24','command':'CLI_PYTHON scripts/ci/cli_drift.py; .github/workflows/cli-drift.yml', 'result':'PARTIAL','date':DATE,'detail':'Local pinned required-flag renderer exercised; Tuesday schedule/hosted issue creation not executed locally.','owner':'repository CI maintainers'},
        {'id':'V27','command':host.get('command','claude plugin eval . --threshold 0.8'),'result':host['status'].upper(),'date':host['date'],'detail':host['reason']+' See evals/results/host.json. No qualifying host task score.','owner':'evaluation maintainers / installed host provider'},
        {'id':'V28','command':'uv run --frozen --project runtime python scripts/eval/head_to_head.py','result':'PARTIAL','date':DATE,'detail':'Four offline arms and a separate controlled model-backed synthetic MCP measurement are recorded. See docs/tool-task-benchmark.md for 160 attempts, grades, costs and limitations. Original native four-product deployment comparison remains unmeasured.','owner':'evaluation maintainers'},
    ])
    # An unavailable provider is no longer the only explanation: the paired
    # alternative was executed and independently syntax-adjudicated. Its
    # limited score cannot become PASS without the original semantic rubric.
    try:
        audit=json.loads((ROOT/'evals/results/native-reference-command-audit-2026-09-11.json').read_text())
        arm=audit['arms']['native-plugin']
        native=next(r for r in rows if r['id']=='V27')
        native.update(result=reference_task_status(audit),owner='evaluation maintainers',
            detail=f"Native evaluator remains early-access restricted. Reference-enabled paired alternative: {arm['passed']}/{arm['attempts']} after pinned syntax adjudication; minimum 80%. Original-task semantics remain a separate requirement. See docs/native-reference-validation-2026-09-11.md.")
    except (OSError,ValueError,KeyError,TypeError):
        pass
    # The opt-in checker is a different, explicitly labelled workflow. Preserve
    # the earlier failure and require its integrity too; neither is full semantics.
    try:
        checked=json.loads((ROOT/'evals/results/checked-task-benchmark-2026-09-11.json').read_text())
        arm=checked['arms']['native-plugin']
        native=next(r for r in rows if r['id']=='V27')
        native.update(result=reference_task_status(checked),owner='evaluation maintainers',
            detail=f"Opt-in checked-command workflow: {arm['passed']}/{arm['attempts']}; minimum 80%. Earlier reference-only workflow remains 29/40. Fixture answers and observed offline command checks are measured, not complete query semantics or live execution. Native evaluator remains early-access restricted. See docs/checked-task-validation-2026-09-11.md.")
    except (OSError,ValueError,KeyError,TypeError):
        pass
    publication=ROOT/'docs/evidence/hosted-drift-publication-2026-09-11.json'
    if publication.exists():
        record=json.loads(publication.read_text())
        if record.get('conclusion')=='success' and record.get('notification',{}).get('published'):
            next(r for r in rows if r['id']=='V24')['detail']='Local drift check and recorded hosted issue publication passed; actual Tuesday scheduler event remains unobserved. See docs/evidence/hosted-drift-publication-2026-09-11.json.'
    extras={r['id']:r for r in rows if '-' in r['id']}
    rows=[r for r in rows if '-' not in r['id']]
    for parent,sub in [('V16','V16-regeneration'),('V16','V16-read-contracts'),('V22','V22-history'),('V24','V24-local'),('V27','V27-reference'),('V27','V27-syntax'),('V27','V27-checked'),('V27','V27-checked-syntax'),('V28','V28-offline'),('V28','V28-fixtures')]:
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
    (output/'docs/evidence/validation-matrix.json').write_text(json.dumps(report,indent=2)+'\n')
    readiness = 'Release-ready.' if report['ready'] else 'Not release-ready.'
    text=f"# Final validation matrix — {DATE}\n\nBranch: `{report['branch']}`. **{readiness}** No tenancy mutations.\n\n"
    text+='Reproduce: `uv run --frozen --project runtime python scripts/ci/release_gate.py --live --links --live-help`. Writes scratch evidence outside the checkout and prints unified diffs against tracked reports. This repeats only scoped read operations and public documentation GETs; skill prerequisites may remain blocked. Omit these flags to reuse dated live/link evidence and use snapshot fence lint. CLI_PYTHON denotes Python from the pinned OCI CLI installation; pass --cli-python to select it explicitly. A nonzero exit is expected while any gate remains red or unmeasured.\n\n'
    text+='| Gate | Command | Result | Date | Evidence / reason / owner |\n|---|---|---|---|---|\n'
    for row in rows:
        detail=row['detail']+(' Owner: '+row['owner']+'.' if row.get('owner') else '')
        text+='| '+row['id']+' | `'+row['command'].replace('|','\\|')+'` | '+row['result']+' | '+row['date']+' | '+detail.replace('|','\\|')+' |\n'
    text+='\nPASS refers to the stated scope. V8 is the current measured OCI-leaf matrix; it does not measure non-OCI rules. V19/V20 verify dated semantic-description selections and their input hashes; CI does not rerun inference. V24 is not a hosted schedule run. V27 has a limited paired alternative measurement, not full original-task certification; native behavioral V28 remains unmeasured. V25/V26 verify bounded selected reads, not deployed workloads or complete inventories. The distributed tree is checked before any uv-created environment symlinks.\n'
    (output/'docs/validation-matrix.md').write_text(text)
    drift = diff_evidence(output)
    print(json.dumps({'ready':report['ready'],'output_dir':str(output),'drift':drift,'nonpassing':[r['id'] for r in rows if r['result']!='PASS']},indent=2))
    return int(not report['ready'] or bool(drift))


if __name__=='__main__':raise SystemExit(main())
