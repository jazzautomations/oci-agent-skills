"""Verify recorded reference-enabled native measurements without inference or OCI."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path, PurePosixPath

import native_reference_benchmark as benchmark


def verify(report):
    tasks = {t['id']: t for t in json.loads((benchmark.ROOT / 'evals/tasks.json').read_text())}
    fixtures = {c['id']: c for c in json.loads((benchmark.ROOT / 'evals/tool-task-fixtures.json').read_text())['cases']}
    rows = report['results']
    if report.get('preflight') is not False:
        raise ValueError('Preflight is not a paired measurement')
    if Counter((r['case'], r['arm']) for r in rows) != Counter((case, arm) for case in tasks for arm in benchmark.ARMS):
        raise ValueError('Missing/repeated pair')
    if report['source_sha256'] != benchmark.fingerprints():
        raise ValueError('Source fingerprints changed or omitted')
    if (report['model'], report['effort'], report['order_seed'], report['runs_per_task_arm'], report['fresh_copy_symlinks']) != (benchmark.MODEL, 'low', 83, 1, 0):
        raise ValueError('Protocol changed')
    if report['attempt_cap_usd'] != benchmark.CAP or report['reservation_per_attempt_usd'] != benchmark.RESERVATION:
        raise ValueError('Budget protocol changed')
    if not 0.25 <= report['budget_usd'] <= 6:
        raise ValueError('Collection budget changed')
    for row in rows:
        if row['input_sha256'] != benchmark.original.digest(benchmark.original.payload(tasks[row['case']], fixtures[row['case']])):
            raise ValueError('Original task changed')
        native = row['arm'] == 'native-plugin'
        allowed = {'StructuredOutput', 'mcp__fixture__read_observation'} | ({'Skill', 'Read'} if native else set())
        if set(row['initialized_tools']) - allowed or 'mcp__fixture__read_observation' not in row['initialized_tools']:
            raise ValueError('Tool surface changed')
        if row['model'] != benchmark.MODEL or any(c['name'] not in allowed for c in row['calls']):
            raise ValueError('Model or call changed')
        plugins = [{'name': 'oci-agent-skills', 'version': '0.2.1'}] if native else []
        if row['plugins'] != plugins or row['plugin_skill_count'] != (37 if native else 0):
            raise ValueError('Plugin isolation changed')
        options = row['launch_options']
        if '--restricted' not in options or '--strict-mcp-config' not in options:
            raise ValueError('Restricted launch absent')
        if options[options.index('--setting-sources') + 1] != '' or options[options.index('--permission-prompts') + 1] != 'none':
            raise ValueError('Settings or permissions changed')
        expected_options = benchmark.native_options(Path('$PLUGIN'), Path('$SESSION')) if native else [
            '--tools', '', '--allowedTools', 'mcp__fixture__read_observation']
        start = options.index('--tools')
        if options[start:start + len(expected_options)] != expected_options:
            raise ValueError('Read directories or tool grants changed')
        expected_launch = ['--restricted', '--setting-sources', '', *expected_options,
            '--strict-mcp-config', '--mcp-config', '$FIXED_FIXTURE_CONFIG',
            '--permission-prompts', 'none', '--no-session-persistence',
            '--model', benchmark.MODEL, '--effort', 'low', '--max-budget-usd', str(benchmark.CAP),
            '--json-schema', json.dumps(benchmark.original.payload(tasks[row['case']], fixtures[row['case']])['output_schema']),
            '--output-format', 'stream-json', '--verbose', '--system-prompt', benchmark.SYSTEM, '-p']
        if options != expected_launch:
            raise ValueError('Unexpected launch option or duplicate override')
        if options[options.index('--system-prompt') + 1] != benchmark.SYSTEM:
            raise ValueError('Collection instructions changed')
        if json.loads(options[options.index('--json-schema') + 1]) != benchmark.original.payload(tasks[row['case']], fixtures[row['case']])['output_schema']:
            raise ValueError('Answer schema changed')
        skill_calls = [c for c in row['calls'] if c['name'] == 'Skill']
        if row['native_skill_activated'] != any(c['result_success'] for c in skill_calls):
            raise ValueError('Activation mismatch')
        if any(not c['input'].get('skill', '').startswith('oci-agent-skills:') for c in skill_calls) and row['completed']:
            raise ValueError('Unqualified invocation must retain protocol failure')
        reads = [c for c in row['calls'] if c['name'] == 'Read']
        for call in reads:
            path = PurePosixPath(call['input'].get('file_path', ''))
            permitted = '..' not in path.parts and len(path.parts) > 2 and path.parts[:2] in {
                ('$PLUGIN', 'skills'), ('$PLUGIN', 'references')}
            if call['within_reference_scope'] != permitted:
                raise ValueError('Read scope evidence mismatch')
            if call['result_success'] and not permitted:
                raise ValueError('Out-of-scope read succeeded')
        if row['successful_reference_reads'] != sum(bool(c['result_success'] and c['within_reference_scope']) for c in reads) or row['out_of_scope_read_succeeded']:
            raise ValueError('Read aggregate mismatch')
        topics = [c['input']['topic'] for c in row['calls'] if c['name'] == 'mcp__fixture__read_observation']
        if Counter(topics) != Counter(r['topic'] for r in row['receipts']):
            raise ValueError('Fixture receipts differ')
        if row['completed']:
            if row['result_subtype'] != 'success':
                raise ValueError('Completion mismatch')
            grades = benchmark.original.score(fixtures[row['case']], row['answer'], row['receipts'])
            if any(row[k] != v for k, v in grades.items()):
                raise ValueError('Grade changed')
        elif row['passed']:
            raise ValueError('Incomplete attempt cannot pass')
    if report['arms'] != benchmark.original.aggregate(rows) or not report['collected_all'] or report.get('stopped_reason'):
        raise ValueError('Incomplete/changed aggregation')
    if report['all_responses_completed'] != all(r['completed'] for r in rows):
        raise ValueError('Completion aggregate mismatch')
    costs = [r.get('cost_usd') for r in rows]
    if any(not isinstance(c, (int, float)) or isinstance(c, bool) or not math.isfinite(c) or c < 0 for c in costs):
        raise ValueError('Missing billing evidence')
    if not math.isclose(sum(costs), report['reported_cost_usd'], rel_tol=0, abs_tol=1e-9):
        raise ValueError('Cost aggregate mismatch')
    for index in range(0, len(rows), 2):
        if not benchmark.can_admit(rows[:index], min(2, len(rows) - index), report['budget_usd']):
            raise ValueError('Admission exceeded collection budget')
    return {'verified': True, 'arms': report['arms'], 'reported_cost_usd': sum(costs),
            'successful_reference_reads': sum(r['successful_reference_reads'] for r in rows),
            'scope': 'Recorded synthetic evidence only; not a query-semantics, live-workload or release certificate.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(json.loads(args.report.read_text())), indent=2))


if __name__ == '__main__':
    main()
