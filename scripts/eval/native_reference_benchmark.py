"""Reference-enabled paired native benchmark; no cloud or model-command execution.

Preserves the earlier collector and grades. Read is confined by the host's
restricted mode to an empty working directory plus skills/ and references/.
Golden fixtures stay outside those directories and are served only by fixed MCP.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import time

import native_task_benchmark as original

ROOT = original.ROOT
MODEL = original.MODEL
ARMS = original.ARMS
CAP = 0.10
# Host cost limits are checked between model requests, not hard billing ceilings.
RESERVATION = 0.25
SYSTEM = original.SYSTEM.replace(
    'No real OCI credentials, shell, browsing, file access or cloud writes are authorized.',
    'No real OCI credentials, shell, browsing or cloud writes are authorized. '
    'When skills are available, Read may access only the installed skills/ and '
    'references/ trees. Follow relevant reference links as needed. Never read '
    'evals, fixture source, reports, session files or files outside those two trees.')


def source_paths():
    paths = [*original.source_paths(), Path(__file__)]
    paths += [p for tree in ('skills', 'references') for p in (ROOT / tree).rglob('*')
              if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    return sorted(set(paths))


def fingerprints():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in source_paths()}


def approved_read(path, plugin):
    resolved = Path(path).resolve()
    return any(resolved.is_relative_to((plugin / name).resolve())
               for name in ('skills', 'references'))


def native_options(plugin, working):
    # --restricted refuses file reads outside working/additional directories,
    # even if an allow rule matches. Never add the whole plugin directory.
    return ['--tools', 'Skill,Read', '--add-dir', str(plugin / 'skills'),
            str(plugin / 'references'), '--allowedTools',
            'Skill(oci-agent-skills:*)', f'Read(/{plugin}/skills/**)',
            f'Read(/{plugin}/references/**)', 'mcp__fixture__read_observation',
            '--disallowedTools', f'Read(/{working}/**)',
            f'Read(/{plugin}/evals/**)', f'Read(/{plugin}/docs/**)',
            f'Read(/{plugin}/scripts/**)', '--plugin-dir', str(plugin)]


def normalize(value, plugin, working):
    if isinstance(value, str):
        return value.replace(str(plugin), '$PLUGIN').replace(str(working), '$SESSION')
    if isinstance(value, list):
        return [normalize(v, plugin, working) for v in value]
    if isinstance(value, dict):
        return {k: normalize(v, plugin, working) for k, v in value.items()}
    return value


def attempt(job, plugin, archive, probe=False):
    task, fixture, arm = job
    request = original.payload(task, fixture)
    if probe:
        request['request'] = (
            'This is a file-access preflight, not the identity benchmark. Use Read '
            f'on {plugin}/references/service-command-cards.md, then use Read on '
            f'{plugin}/evals/ACCESS-CANARY.txt exactly once. The second file is a '
            'harmless canary whose read should be blocked by host permissions. '
            'Both calls are required to measure access; do not skip either. '
            'After those two calls, complete this synthetic task: ' + task['prompt'])
    row = {'case': task['id'], 'arm': arm, 'input_sha256': original.digest(request),
           'completed': False, 'passed': False}
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='oci-reference-session-') as directory:
        working = Path(directory)
        # Keep receipts outside the session's readable working directory too.
        trace = archive / f"{task['id']}-{arm}.receipts.jsonl"
        transcript = archive / f"{task['id']}-{arm}.stream.jsonl"
        if transcript.exists() or trace.exists():
            raise ValueError('Private evidence already exists')
        config = {'mcpServers': {'fixture': {'command': sys.executable,
            'args': [str(plugin / 'scripts/eval/tool_fixture_server.py')],
            'env': {'OCI_FIXTURE_TRACE': str(trace)}}}}
        env = {k: v for k, v in os.environ.items()
               if not k.startswith('OCI_') and k not in {'CLAUDECODE', 'CLAUDE_CODE_SAFE_MODE'}}
        env.update(OCI_CONFIG_FILE=directory + '/absent', OCI_CLI_CONFIG_FILE=directory + '/absent')
        options = native_options(plugin, working) if arm == 'native-plugin' else [
            '--tools', '', '--allowedTools', 'mcp__fixture__read_observation']
        system = SYSTEM
        if probe:
            system += (' This is an access preflight, excluded from benchmark scores. '
                       f'First read {plugin}/references/service-command-cards.md. '
                       f'Then attempt to read {plugin}/evals/ACCESS-CANARY.txt exactly once; '
                       'the latter must be denied. Continue the task after that denial.')
        argv = ['claude', '--restricted', '--setting-sources', '', *options,
                '--strict-mcp-config', '--mcp-config', json.dumps(config),
                '--permission-prompts', 'none', '--no-session-persistence',
                '--model', MODEL, '--effort', 'low', '--max-budget-usd', str(CAP),
                '--json-schema', json.dumps(request['output_schema']),
                '--output-format', 'stream-json', '--verbose', '--system-prompt', system, '-p']
        row['launch_options'] = normalize(argv[1:], plugin, working)
        # MCP config contains private trace paths; record its fixed structure separately.
        row['launch_options'][row['launch_options'].index('--mcp-config') + 1] = '$FIXED_FIXTURE_CONFIG'
        try:
            proc = subprocess.run(argv, input=json.dumps(request), cwd=directory, env=env,
                                  text=True, capture_output=True, timeout=180)
            transcript.write_text(proc.stdout)
            transcript.chmod(0o600)
            row['transcript_sha256'] = hashlib.sha256(proc.stdout.encode()).hexdigest()
            events = [json.loads(x) for x in proc.stdout.splitlines() if x.strip()]
            init = next(e for e in events if e.get('type') == 'system' and e.get('subtype') == 'init')
            result = next(e for e in reversed(events) if e.get('type') == 'result')
            contents = [c for e in events for c in e.get('message', {}).get('content', []) if isinstance(c, dict)]
            outcomes = {c['tool_use_id']: not c.get('is_error', False)
                        for c in contents if c.get('type') == 'tool_result'}
            calls = [{'name': c['name'], 'input': c['input'], 'result_success': outcomes.get(c['id'])}
                     for c in contents if c.get('type') == 'tool_use']
            reads = [c for c in calls if c['name'] == 'Read']
            for call in reads:
                call['within_reference_scope'] = approved_read(call['input'].get('file_path', ''), plugin)
            row.update(cost_usd=result.get('total_cost_usd'), duration_ms=result.get('duration_ms'),
                usage=result.get('usage'), host_version=init.get('claude_code_version'),
                model=init.get('model'), result_subtype=result.get('subtype'),
                initialized_tools=init.get('tools'),
                plugins=[{'name': p['name'], 'version': p.get('version')} for p in init.get('plugins', [])],
                plugin_skill_count=sum(s.startswith('oci-agent-skills:') for s in init.get('skills', [])),
                calls=normalize(calls, plugin, working),
                receipts=[json.loads(x) for x in trace.read_text().splitlines()] if trace.exists() else [],
                native_skill_activated=any(c['name'] == 'Skill' and c['result_success'] for c in calls),
                successful_reference_reads=sum(bool(c['result_success'] and c['within_reference_scope']) for c in reads),
                out_of_scope_read_succeeded=any(c['result_success'] and not c['within_reference_scope'] for c in reads))
            allowed = {'StructuredOutput', 'mcp__fixture__read_observation'} | ({'Skill', 'Read'} if arm == 'native-plugin' else set())
            if init.get('model') != MODEL or set(init.get('tools', [])) - allowed:
                raise ValueError('Tool/model surface')
            if any(c['name'] not in allowed for c in calls) or row['out_of_scope_read_succeeded']:
                raise ValueError('Unexpected capability or read')
            if any(not c['input'].get('skill', '').startswith('oci-agent-skills:') for c in calls if c['name'] == 'Skill'):
                raise ValueError('Unqualified skill activation retained as protocol failure')
            expected_plugins = [{'name': 'oci-agent-skills', 'version': '0.2.1'}] if arm == 'native-plugin' else []
            if row['plugins'] != expected_plugins or row['plugin_skill_count'] != (37 if arm == 'native-plugin' else 0):
                raise ValueError('Plugin isolation')
            if probe:
                row['access_probe_passed'] = bool(row['successful_reference_reads'] and any(
                    c['input'].get('file_path', '').endswith('/evals/ACCESS-CANARY.txt')
                    and c['result_success'] is False for c in reads))
            if proc.returncode or result.get('is_error') or result.get('subtype') != 'success':
                raise ValueError('Incomplete attempt')
            answer = normalize(result['structured_output'], plugin, working)
            row.update(answer=answer, completed=True, **original.score(fixture, answer, row['receipts']))
        except (ValueError, KeyError, StopIteration, TypeError, OSError, subprocess.TimeoutExpired):
            row['error'] = 'Incomplete or invalid attempt retained without retry.'
    row['wall_duration_seconds'] = round(time.monotonic() - started, 3)
    return row


def can_admit(rows, count, budget):
    costs = [r.get('cost_usd') for r in rows]
    if any(not isinstance(c, (int, float)) or isinstance(c, bool) or not math.isfinite(c) or c < 0 for c in costs):
        return False
    return sum(costs) + RESERVATION * count <= budget


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--collect', action='store_true')
    p.add_argument('--preflight', action='store_true')
    p.add_argument('--report', type=Path, required=True)
    p.add_argument('--archive', type=Path)
    p.add_argument('--budget-usd', type=float, default=6)
    a = p.parse_args()
    if not math.isfinite(a.budget_usd) or not 0.25 <= a.budget_usd <= 6:
        p.error('Collection budget must be between 0.25 and 6 USD; not a renewed user budget')
    if not a.collect:
        print(json.dumps({'attempts': 1 if a.preflight else 80, 'budget_usd': a.budget_usd, 'model_calls': 0, 'cloud_calls': 0}))
        return 0
    if a.report.exists() or not a.archive or a.archive.exists():
        p.error('Require new report and private archive paths')
    a.archive.mkdir(parents=True, mode=0o700)
    tasks = json.loads((ROOT / 'evals/tasks.json').read_text())
    fixtures = {c['id']: c for c in json.loads((ROOT / 'evals/tool-task-fixtures.json').read_text())['cases']}
    imported = json.loads((ROOT / 'evals/evals.json').read_text())['evals']
    if {t['id']: t['prompt'] for t in tasks} != {t['id']: t['prompt'] for t in imported}:
        raise ValueError('Original prompt mismatch')
    jobs = [(t, fixtures[t['id']], arm) for t in tasks for arm in ARMS]
    random.Random(83).shuffle(jobs)
    if a.preflight:
        jobs = [(tasks[0], fixtures[tasks[0]['id']], 'native-plugin')]
    report = {'date': datetime.now(timezone.utc).isoformat(), 'model': MODEL,
        'effort': 'low', 'order_seed': 83, 'runs_per_task_arm': 1,
        'source_sha256': fingerprints(), 'budget_usd': a.budget_usd,
        'attempt_cap_usd': CAP, 'reservation_per_attempt_usd': RESERVATION,
        'preflight': a.preflight, 'results': [],
        'scope': 'Fresh native Skill plus restricted Read of shipped skills/references, '
        'versus no-plugin sessions; fixed synthetic MCP observations. Exact original '
        'answer/receipt/proposed-command grades retained. No model commands, OCI '
        'operations, live mutation defense or native competitor servers are executed. '
        'Preflight is excluded from task scores; one repetition cannot estimate run variance.'}
    with tempfile.TemporaryDirectory(prefix='oci-reference-install-') as directory:
        plugin = Path(directory) / 'plugin'
        subprocess.run(['bash', str(ROOT / 'installers/install.sh'), '--target', str(plugin),
                        '--host', 'claude', '--copy-shared'], check=True, capture_output=True)
        if any(p.is_symlink() for p in plugin.rglob('*')):
            raise ValueError('Fresh distribution contains symlinks')
        report['fresh_copy_symlinks'] = 0
        if a.preflight:
            (plugin / 'evals/ACCESS-CANARY.txt').write_text('Harmless forbidden-access canary.\n')
        a.report.parent.mkdir(parents=True, exist_ok=True)
        with ThreadPoolExecutor(max_workers=2) as pool:
            for offset in range(0, len(jobs), 2):
                batch = jobs[offset:offset + 2]
                if not can_admit(report['results'], len(batch), a.budget_usd):
                    report['stopped_reason'] = 'Budget reservation or missing billing evidence; no retry.'
                    break
                for row in pool.map(lambda job: attempt(job, plugin, a.archive, a.preflight), batch):
                    report['results'].append(row)
                    print(json.dumps({k: row.get(k) for k in ('case', 'arm', 'completed', 'passed', 'successful_reference_reads', 'cost_usd', 'access_probe_passed')}), flush=True)
                report['arms'] = original.aggregate(report['results'])
                report['collected_all'] = len(report['results']) == len(jobs)
                report['all_responses_completed'] = all(r['completed'] for r in report['results'])
                report['reported_cost_usd'] = sum(r.get('cost_usd') or 0 for r in report['results'])
                a.report.write_text(json.dumps(report, indent=2) + '\n')
                if any(r.get('out_of_scope_read_succeeded') for r in report['results']):
                    report['stopped_reason'] = 'Read isolation failure; no further calls.'
                    break
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    return int(not report.get('collected_all') or bool(report.get('stopped_reason')))


if __name__ == '__main__':
    raise SystemExit(main())
