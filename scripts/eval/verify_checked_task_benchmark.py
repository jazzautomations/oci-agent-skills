"""Recompute checked-task evidence offline; never infer or execute OCI proposals."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path, PurePosixPath

import checked_task_benchmark as benchmark


def verify(report):
    if report.get('preflight') is not False or not report.get('collected_all') or report.get('stopped_reason'):
        raise ValueError('Not a complete paired measurement')
    tasks = {t['id']: t for t in json.loads((benchmark.ROOT / 'evals/tasks.json').read_text())}
    fixtures = {r['id']: r for r in json.loads((benchmark.ROOT / 'evals/tool-task-fixtures.json').read_text())['cases']}
    rows = report['results']
    if Counter((r['case'], r['arm']) for r in rows) != Counter((case, arm) for case in tasks for arm in benchmark.ARMS):
        raise ValueError('Missing/duplicate task-arm pair')
    if report['source_sha256'] != benchmark.fingerprints():
        raise ValueError('Source changed or omitted')
    if (report['model'], report['effort'], report['order_seed'], report['runs_per_task_arm'], report['fresh_copy_symlinks']) != (benchmark.MODEL, 'low', 83, 1, 0):
        raise ValueError('Protocol changed')
    if report['attempt_cap_usd'] != benchmark.CAP or report['reservation_per_attempt_usd'] != benchmark.previous.RESERVATION or not .5 <= report['budget_usd'] <= 5:
        raise ValueError('Budget changed')
    for row in rows:
        native = row['arm'] == 'native-plugin'
        request = benchmark.previous.original.payload(tasks[row['case']], fixtures[row['case']])
        if row['input_sha256'] != benchmark.previous.original.digest(request):
            raise ValueError('Original prompt/schema changed')
        options = benchmark.previous.native_options(Path('$PLUGIN'), Path('$SESSION')) if native else [
            '--tools', '', '--allowedTools', 'mcp__fixture__read_observation']
        index = options.index('--allowedTools') + 1
        options[index:index] = sorted(benchmark.CONTRACT_TOOLS)
        launch = ['--restricted', '--setting-sources', '', *options,
            '--strict-mcp-config', '--mcp-config', '$FIXED_FIXTURE_AND_CONTRACT_CONFIG',
            '--permission-prompts', 'none', '--no-session-persistence', '--model', benchmark.MODEL,
            '--effort', 'low', '--max-budget-usd', str(benchmark.CAP), '--json-schema', json.dumps(request['output_schema']),
            '--output-format', 'stream-json', '--verbose', '--system-prompt', benchmark.SYSTEM, '-p']
        if row['launch_options'] != launch:
            raise ValueError('Capability or instruction changed')
        allowed = {'StructuredOutput', 'mcp__fixture__read_observation'} | benchmark.CONTRACT_TOOLS | ({'Read', 'Skill'} if native else set())
        if row['model'] != benchmark.MODEL or set(row['initialized_tools']) != allowed or any(c['name'] not in allowed for c in row['calls']):
            raise ValueError('Model or tools changed')
        expected_plugins = [{'name': 'oci-agent-skills', 'version': '0.2.1'}] if native else []
        if row['plugins'] != expected_plugins:
            raise ValueError('Plugin isolation')
        registered = row['registered_skills']
        expected_names = {'oci-agent-skills:' + p.parent.name for p in (benchmark.ROOT / 'skills').glob('*/SKILL.md')}
        if native and not expected_names <= set(registered) or not native and (registered or row['loaded_skills']):
            raise ValueError('Skill registration mismatch')
        resolutions = [{'requested': c['input'].get('skill', ''), 'canonical': benchmark.resolve_skill(
            c['input'].get('skill', ''), registered, row['loaded_skills']), 'result_success': c['result_success']}
            for c in row['calls'] if c['name'] == 'Skill']
        if resolutions != row['skill_resolutions'] or row['native_skill_activated'] != any(r['canonical'] and r['result_success'] for r in resolutions):
            raise ValueError('Skill identity mismatch')
        if row['completed'] and any(not r['canonical'] for r in resolutions):
            raise ValueError('Unverified alias cannot pass')
        reads = [c for c in row['calls'] if c['name'] == 'Read']
        for call in reads:
            path = PurePosixPath(call['input'].get('file_path', ''))
            scoped = '..' not in path.parts and path.parts[:2] in {('$PLUGIN', 'skills'), ('$PLUGIN', 'references')}
            if call['within_reference_scope'] != scoped or call['result_success'] and not scoped:
                raise ValueError('Unexpected read')
        if row['successful_reference_reads'] != sum(bool(c['result_success'] and c['within_reference_scope']) for c in reads):
            raise ValueError('Read count mismatch')
        topics = [c['input']['topic'] for c in row['calls'] if c['name'] == 'mcp__fixture__read_observation']
        if Counter(topics) != Counter(r['topic'] for r in row['receipts']):
            raise ValueError('Receipt mismatch')
        if row['completed']:
            if not row['host_completed'] or row['result_subtype'] != 'success':
                raise ValueError('Host completion mismatch')
            grades = benchmark.score(fixtures[row['case']], row['answer'], row['receipts'], row['calls'])
            if any(row[k] != value for k, value in grades.items()):
                raise ValueError('Score changed')
        elif row['passed']:
            raise ValueError('Incomplete attempt cannot pass')
    costs = [r.get('cost_usd') for r in rows]
    if any(not isinstance(c, (int, float)) or isinstance(c, bool) or not math.isfinite(c) or c < 0 for c in costs):
        raise ValueError('Missing billing evidence')
    if not math.isclose(sum(costs), report['reported_cost_usd'], rel_tol=0, abs_tol=1e-9):
        raise ValueError('Cost mismatch')
    for index in range(0, len(rows), 2):
        if not benchmark.previous.can_admit(rows[:index], 2, report['budget_usd']):
            raise ValueError('Admission budget violated')
    if report['arms'] != benchmark.previous.original.aggregate(rows):
        raise ValueError('Aggregate mismatch')
    return {'verified': True, 'arms': report['arms'], 'reported_cost_usd': sum(costs),
            'scope': 'Exact fixture answers and checked inert commands, not full query semantics or OCI execution.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(json.loads(args.report.read_text())), indent=2))


if __name__ == '__main__':
    main()
