"""Verify recorded native-host fixture evidence without model or cloud calls."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

import native_task_benchmark as benchmark


def verify(report):
    tasks = {t['id']: t for t in json.loads((benchmark.ROOT / 'evals/tasks.json').read_text())}
    fixtures = {c['id']: c for c in json.loads((benchmark.ROOT / 'evals/tool-task-fixtures.json').read_text())['cases']}
    rows = report['results']
    if Counter((r['case'], r['arm']) for r in rows) != Counter((case, arm) for case in tasks for arm in benchmark.ARMS):
        raise ValueError('Missing/repeated task-arm pair')
    sources = {str(p.relative_to(benchmark.ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in benchmark.source_paths()}
    if sources != report['source_sha256']:
        raise ValueError('Source fingerprints changed or omitted')
    if (report['model'], report['effort'], report['order_seed'], report['runs_per_task_arm'], report['fresh_copy_symlinks']) != (benchmark.MODEL, 'low', 83, 1, 0):
        raise ValueError('Protocol changed')
    for row in rows:
        if row['input_sha256'] != benchmark.digest(benchmark.payload(tasks[row['case']], fixtures[row['case']])):
            raise ValueError('Task input changed')
        native = row['arm'] == 'native-plugin'
        allowed = {'StructuredOutput', 'mcp__fixture__read_observation'} | ({'Skill'} if native else set())
        # Validate all captured attempts, including retained protocol rejections.
        if set(row['initialized_tools']) - allowed or 'mcp__fixture__read_observation' not in row['initialized_tools']:
            raise ValueError('Unexpected tool surface')
        if row['model'] != benchmark.MODEL or any(c['name'] not in allowed for c in row['calls']):
            raise ValueError('Unexpected model/tool call')
        expected_plugins = [{'name': 'oci-agent-skills', 'version': '0.2.1'}] if native else []
        if row['plugins'] != expected_plugins or row['plugin_skill_count'] != (37 if native else 0):
            raise ValueError('Plugin isolation changed')
        skill_calls = [c for c in row['calls'] if c['name'] == 'Skill']
        rejected_skill = any(not c['input'].get('skill', '').startswith('oci-agent-skills:') for c in skill_calls)
        if rejected_skill:
            if row['completed'] or row['passed'] or 'native_skill_activated' in row or not row.get('error'):
                raise ValueError('Unqualified skill must retain protocol rejection')
        elif row.get('native_skill_activated') != any(c['result_success'] for c in skill_calls):
            raise ValueError('Activation mismatch')
        topics = [c['input']['topic'] for c in row['calls'] if c['name'] == 'mcp__fixture__read_observation']
        if Counter(topics) != Counter(r['topic'] for r in row['receipts']):
            raise ValueError('Receipts and tool calls differ')
        if row['completed']:
            if row['result_subtype'] != 'success':
                raise ValueError('Completion mismatch')
            grades = benchmark.score(fixtures[row['case']], row['answer'], row['receipts'])
            if any(row[k] != v for k, v in grades.items()):
                raise ValueError('Changed score')
        elif row['passed']:
            raise ValueError('Incomplete attempt cannot pass')
    arms = benchmark.aggregate(rows)
    if report['arms'] != arms or report['collected_all'] is not True or report['all_responses_completed'] != all(r['completed'] for r in rows):
        raise ValueError('Aggregate mismatch')
    costs = [r.get('cost_usd') for r in rows]
    if any(not isinstance(c, (int, float)) or isinstance(c, bool) or not math.isfinite(c) or c < 0 for c in costs):
        raise ValueError('Missing/invalid cost')
    if not math.isclose(sum(costs), report['reported_cost_usd'], rel_tol=0, abs_tol=1e-9):
        raise ValueError('Cost aggregate mismatch')
    return {'verified': True, 'arms': arms, 'reported_cost_usd': sum(costs),
            'scope': 'Recorded fixture answers, native activation and original inert-command grades only. Consult the separate syntax adjudication; this is not a full live-workload or V27 certificate.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(json.loads(args.report.read_text())), indent=2))


if __name__ == '__main__':
    main()
