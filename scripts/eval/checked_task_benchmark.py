"""Paired native tasks with the shipped offline command-contract MCP, no OCI execution."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import time

import native_reference_benchmark as previous
from read_contract import check

ROOT = previous.ROOT
MODEL = previous.MODEL
ARMS = previous.ARMS
CAP = 0.12
SYSTEM = previous.SYSTEM + (
    ' Use the offline command-contract tools to inspect exact flags; they never execute commands. '
    'Before finalizing, call check_read_command on EACH proposed command. Repair invalid proposals '
    'using describe_read_command and check again; do not send invalid commands as a finished result. '
    'Use canonical long option names, never assume aliases exist on another command. '
    'Use one bounded page (1..100 items) and no --all; do not claim that a bounded page is a complete inventory. '
    'Where a leaf has no --limit, do not invent it; use the stated time/resource scope. '
    'Only include entities satisfying the requested filter. Missing entities are not invented entries. '
    'Structured lists of findings or names contain literal identifying values from observations, '
    'not explanatory paragraphs or non-findings. Do not add facts from irrelevant observations. '
    'If a native plugin is available, activate a relevant registered OCI skill; use its references '
    'when needed. Qualified names are preferred. No gold answers or evaluator files are readable.')
CONTRACT_TOOLS = {'mcp__contract__describe_read_command', 'mcp__contract__check_read_command'}


def sources():
    return sorted(set(previous.source_paths() + [Path(__file__), ROOT / 'scripts/read_contract.py',
        ROOT / 'scripts/command_contract_server.py', ROOT / 'scripts/generate_read_contracts.py',
        ROOT / 'catalog/read-contracts.json', ROOT / 'runtime/pyproject.toml', ROOT / 'runtime/uv.lock']))


def fingerprints():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources()}


def resolve_skill(requested, registered, loaded):
    """Unqualified aliases need unique registration AND an observed installed skill body."""
    names = [s for s in registered if s == requested or s.rsplit(':', 1)[-1] == requested]
    if requested.startswith('oci-agent-skills:') and requested in registered:
        return requested
    if ':' not in requested and names == ['oci-agent-skills:' + requested] and requested in loaded:
        return names[0]
    return None


def score(fixture, answer, receipts, calls):
    grades = previous.original.score(fixture, answer, receipts)
    commands = answer.get('commands', []) if isinstance(answer, dict) else []
    checked = {c['input'].get('command') for c in calls
               if c['name'] == 'mcp__contract__check_read_command' and c['result_success']}
    grades['contract_valid'] = all(isinstance(c, str) and check(c)['valid'] for c in commands)
    grades['each_final_command_checked'] = all(c in checked for c in commands)
    grades['passed'] = bool(grades['passed'] and grades['contract_valid'] and grades['each_final_command_checked'])
    return grades


def attempt(job, plugin, archive):
    task, fixture, arm = job
    request = previous.original.payload(task, fixture)
    row = {'case': task['id'], 'arm': arm, 'input_sha256': previous.original.digest(request),
           'completed': False, 'passed': False}
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='oci-checked-session-') as directory:
        working = Path(directory)
        trace = archive / f"{task['id']}-{arm}.receipts.jsonl"
        transcript = archive / f"{task['id']}-{arm}.stream.jsonl"
        if transcript.exists() or trace.exists():
            raise ValueError('Preserve existing private evidence')
        config = {'mcpServers': {
            'fixture': {'command': sys.executable, 'args': [str(plugin / 'scripts/eval/tool_fixture_server.py')],
                        'env': {'OCI_FIXTURE_TRACE': str(trace)}},
            'contract': {'command': sys.executable, 'args': [str(plugin / 'scripts/command_contract_server.py')]}}}
        env = {k: v for k, v in os.environ.items() if not k.startswith('OCI_') and k not in {'CLAUDECODE', 'CLAUDE_CODE_SAFE_MODE'}}
        env.update(OCI_CONFIG_FILE=directory + '/absent', OCI_CLI_CONFIG_FILE=directory + '/absent')
        options = previous.native_options(plugin, working) if arm == 'native-plugin' else [
            '--tools', '', '--allowedTools', 'mcp__fixture__read_observation']
        # Insert into the existing allow-list before the next option, never enable a shell.
        index = options.index('--allowedTools') + 1
        options[index:index] = sorted(CONTRACT_TOOLS)
        argv = ['claude', '--restricted', '--setting-sources', '', *options,
            '--strict-mcp-config', '--mcp-config', json.dumps(config), '--permission-prompts', 'none',
            '--no-session-persistence', '--model', MODEL, '--effort', 'low', '--max-budget-usd', str(CAP),
            '--json-schema', json.dumps(request['output_schema']), '--output-format', 'stream-json',
            '--verbose', '--system-prompt', SYSTEM, '-p']
        row['launch_options'] = previous.normalize(argv[1:], plugin, working)
        row['launch_options'][row['launch_options'].index('--mcp-config') + 1] = '$FIXED_FIXTURE_AND_CONTRACT_CONFIG'
        try:
            proc = subprocess.run(argv, input=json.dumps(request), cwd=directory, env=env, text=True,
                                  capture_output=True, timeout=180)
            transcript.write_text(proc.stdout); transcript.chmod(0o600)
            events = [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]
            init = next(e for e in events if e.get('type') == 'system' and e.get('subtype') == 'init')
            result = next(e for e in reversed(events) if e.get('type') == 'result')
            content = [c for e in events for c in e.get('message', {}).get('content', []) if isinstance(c, dict)]
            outcomes = {c['tool_use_id']: not c.get('is_error', False) for c in content if c.get('type') == 'tool_result'}
            calls = [{'name': c['name'], 'input': c['input'], 'result_success': outcomes.get(c['id'])}
                     for c in content if c.get('type') == 'tool_use']
            loaded = sorted({p.parent.name for p in (plugin / 'skills').glob('*/SKILL.md') if any(
                c.get('type') == 'text' and c.get('text', '').startswith('Base directory for this skill: ' + str(p.parent) + '\n')
                for e in events if e.get('type') == 'user' for c in e.get('message', {}).get('content', []))})
            resolutions = [{'requested': c['input'].get('skill', ''), 'canonical': resolve_skill(
                c['input'].get('skill', ''), init.get('skills', []), loaded), 'result_success': c['result_success']}
                for c in calls if c['name'] == 'Skill']
            packaged_names = {p.parent.name for p in (plugin / 'skills').glob('*/SKILL.md')}
            registered = [s for s in init.get('skills', []) if s.rsplit(':', 1)[-1] in packaged_names]
            reads = [c for c in calls if c['name'] == 'Read']
            for c in reads:
                c['within_reference_scope'] = previous.approved_read(c['input'].get('file_path', ''), plugin)
            row.update(cost_usd=result.get('total_cost_usd'), duration_ms=result.get('duration_ms'),
                usage=result.get('usage'), host_version=init.get('claude_code_version'), model=init.get('model'),
                initialized_tools=init.get('tools'), registered_skills=registered,
                loaded_skills=loaded, skill_resolutions=resolutions,
                plugins=[{'name': p['name'], 'version': p.get('version')} for p in init.get('plugins', [])],
                result_subtype=result.get('subtype'), host_completed=result.get('subtype') == 'success' and not result.get('is_error'),
                calls=previous.normalize(calls, plugin, working),
                receipts=[json.loads(x) for x in trace.read_text().splitlines()] if trace.exists() else [],
                answer=previous.normalize(result.get('structured_output'), plugin, working),
                native_skill_activated=any(r['canonical'] and r['result_success'] for r in resolutions),
                successful_reference_reads=sum(bool(c['result_success'] and c['within_reference_scope']) for c in reads),
                transcript_sha256=hashlib.sha256(proc.stdout.encode()).hexdigest())
            allowed = {'StructuredOutput', 'mcp__fixture__read_observation'} | CONTRACT_TOOLS | ({'Skill', 'Read'} if arm == 'native-plugin' else set())
            if row['model'] != MODEL or set(row['initialized_tools']) != allowed:
                raise ValueError('Tool/model surface')
            if any(c['name'] not in allowed for c in calls) or any(c['result_success'] and not c['within_reference_scope'] for c in reads):
                raise ValueError('Unexpected capability')
            expected = [{'name': 'oci-agent-skills', 'version': '0.2.1'}] if arm == 'native-plugin' else []
            if row['plugins'] != expected or any(not r['canonical'] for r in resolutions):
                raise ValueError('Unverified plugin identity')
            if proc.returncode or not row['host_completed']:
                raise ValueError('Incomplete host result')
            row.update(completed=True, **score(fixture, row['answer'], row['receipts'], calls))
        except (ValueError, TypeError, KeyError, StopIteration, OSError, subprocess.TimeoutExpired):
            row['error'] = 'Incomplete or invalid attempt retained without retry.'
    row['wall_duration_seconds'] = round(time.monotonic() - started, 3)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--collect', action='store_true')
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--budget-usd', type=float, default=5)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--archive', type=Path)
    args = parser.parse_args()
    if not .5 <= args.budget_usd <= 5:
        parser.error('Budget must be 0.5..5 USD, inside the ongoing aggregate ceiling')
    if not args.collect:
        print(json.dumps({'attempts': 2 if args.preflight else 80, 'model_calls': 0, 'cloud_calls': 0})); return 0
    if args.report.exists() or not args.archive or args.archive.exists():
        parser.error('Use new report and archive paths')
    args.archive.mkdir(parents=True, mode=0o700)
    tasks = json.loads((ROOT / 'evals/tasks.json').read_text())
    imported = json.loads((ROOT / 'evals/evals.json').read_text())['evals']
    if {t['id']: t['prompt'] for t in tasks} != {t['id']: t['prompt'] for t in imported}:
        raise ValueError('Original prompts changed')
    fixtures = {r['id']: r for r in json.loads((ROOT / 'evals/tool-task-fixtures.json').read_text())['cases']}
    if args.preflight:
        tasks = tasks[:1]
    jobs = [(t, fixtures[t['id']], arm) for t in tasks for arm in ARMS]
    random.Random(83).shuffle(jobs)
    report = {'date': datetime.now(timezone.utc).isoformat(), 'model': MODEL, 'effort': 'low',
        'order_seed': 83, 'runs_per_task_arm': 1, 'preflight': args.preflight,
        'source_sha256': fingerprints(), 'budget_usd': args.budget_usd, 'attempt_cap_usd': CAP,
        'reservation_per_attempt_usd': previous.RESERVATION, 'results': [],
        'scope': 'Both arms use shipped offline command-contract MCP and identical synthetic observations. '
        'Native plugin plus restricted reference reads versus no plugin. Original exact answers and command '
        'grades retained; additionally require bounded contract-valid final commands and observed checks. '
        'Unique registered Skill aliases require observed installed bodies. No OCI or model-command execution; '
        'not full query semantics, live defense, a holdout or native four-product comparison.'}
    with tempfile.TemporaryDirectory(prefix='oci-checked-install-') as directory:
        plugin = Path(directory) / 'plugin'
        subprocess.run(['bash', str(ROOT / 'installers/install.sh'), '--target', str(plugin), '--host', 'claude', '--copy-shared'], check=True, capture_output=True)
        if any(p.is_symlink() for p in plugin.rglob('*')):
            raise ValueError('Distribution symlink')
        report['fresh_copy_symlinks'] = 0
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with ThreadPoolExecutor(max_workers=2) as pool:
            for offset in range(0, len(jobs), 2):
                batch = jobs[offset:offset + 2]
                if not previous.can_admit(report['results'], len(batch), args.budget_usd):
                    report['stopped_reason'] = 'Budget reservation or missing billing evidence'; break
                for row in pool.map(lambda job: attempt(job, plugin, args.archive), batch):
                    report['results'].append(row)
                    print(json.dumps({k: row.get(k) for k in ('case', 'arm', 'completed', 'passed', 'cost_usd')}), flush=True)
                report['arms'] = previous.original.aggregate(report['results'])
                report['collected_all'] = len(report['results']) == len(jobs)
                report['reported_cost_usd'] = sum(r.get('cost_usd') or 0 for r in report['results'])
                args.report.write_text(json.dumps(report, indent=2) + '\n')
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    return int(not report.get('collected_all') or bool(report.get('stopped_reason')))


if __name__ == '__main__':
    raise SystemExit(main())
