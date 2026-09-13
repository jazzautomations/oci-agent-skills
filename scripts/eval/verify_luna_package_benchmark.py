"""Recompute recorded Luna task scores; no model call or proposed command execution."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import random

import jsonschema
import checked_task_benchmark as benchmark
from audit_query_fields import audit as audit_fields

ARMS = ('pack', 'oracle', 'adibirzu')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def aggregate(rows):
    return {arm: {'submitted': sum(r['arm'] == arm for r in rows),
                  'completed': sum(r['arm'] == arm and r['completed'] for r in rows),
                  'passed': sum(r['arm'] == arm and r['passed'] for r in rows),
                  'cases_with_skill_read': sum(r['arm'] == arm and bool(r['loaded_skills']) for r in rows),
                  'cases_with_reference_read': sum(r['arm'] == arm and bool(r['reference_reads']) for r in rows)}
            for arm in ARMS}


def paired(rows, order):
    by_key = {(r['arm'], r['case']): r for r in rows}
    results = []
    for other in ARMS[1:]:
        cases = [c for c in order if ('pack', c) in by_key and (other, c) in by_key]
        wins = [c for c in cases if by_key['pack', c]['passed'] and not by_key[other, c]['passed']]
        losses = [c for c in cases if not by_key['pack', c]['passed'] and by_key[other, c]['passed']]
        n = len(wins) + len(losses)
        probability = min(1, 2 * sum(math.comb(n, i) for i in range(min(len(wins), len(losses)) + 1)) / 2**n) if n else 1.0
        results.append({'opponent': other, 'paired_cases': len(cases), 'pack_only': wins,
                        'opponent_only': losses, 'p_exact': probability})
    last = 0
    for index, item in enumerate(sorted(results, key=lambda c: c['p_exact'])):
        last = max(last, min(1, (2 - index) * item['p_exact']))
        item['p_holm'] = last
    return results


def verify(report, *, case_ids=None):
    tasks = {t['id']: t for t in json.loads((benchmark.ROOT / 'evals/tasks.json').read_text())}
    if case_ids is not None:
        require(case_ids and len(set(case_ids)) == len(case_ids) and set(case_ids) <= tasks.keys(), 'Invalid explicit test scope')
        tasks = {case: tasks[case] for case in case_ids}
    fixtures = {f['id']: f for f in json.loads((benchmark.ROOT / 'evals/tool-task-fixtures.json').read_text())['cases']}
    require(report['source_sha256'] == benchmark.fingerprints(), 'Source changed or omitted; use the evidence checkout')
    require(report['format_version'] == 1 and report['model'] == 'gpt-5.6-luna', 'Model/format changed')
    order = list(tasks)
    random.Random(915).shuffle(order)
    protocol = report['protocol']
    require(protocol['tasks'] == order and protocol['arms'] == list(ARMS) and
            protocol['order_seed'] == 915 and protocol['runs_per_task_arm'] == 1 and
            protocol['max_actions_per_case'] == 16 and protocol['max_observations_per_case'] == 8 and
            protocol['max_wall_seconds'] == 2700, 'Protocol changed')
    rows = report['results']
    require(Counter((r['case'], r['arm']) for r in rows) == Counter((case, arm) for case in tasks for arm in ARMS)
            and report['collected_all'] is True, 'Missing or duplicate task-arm pair')
    for row in rows:
        require(all(type(row[k]) is bool for k in ('completed', 'passed', 'schema_valid')), 'Outcome flags must be booleans')
        payload = benchmark.previous.original.payload(tasks[row['case']], fixtures[row['case']])
        require(row['input_sha256'] == benchmark.previous.original.digest(payload), 'Original prompt/schema changed')
        events = row['events']
        require(events and len(events) <= 17 and events[-1]['action'] == 'submit' and
                sum(e['action'] == 'submit' for e in events) == 1 and row['action_count'] == len(events) - 1,
                'Submission or action budget mismatch')
        require(all(e['case'] == row['case'] and e['request']['case'] == row['case'] and
                    e['action'] == e['request']['action'] and type(e['success']) is bool and
                    e['action'] in {'activate', 'read', 'list', 'observe', 'describe', 'check', 'submit'} for e in events),
                'Unexpected recorded action')
        require(events[-1]['request']['answer'] == row['answer'], 'Final answer differs from submission')
        receipts = [{'topic': e['request']['topic'], 'ok': True} for e in events if e['action'] == 'observe' and e['success']]
        require(receipts == row['receipts'] and len(receipts) <= 8, 'Receipt mismatch')
        checks = [{'name': 'mcp__contract__check_read_command', 'input': {'command': e['request']['command']},
                   'result_success': e['success']} for e in events if e['action'] == 'check']
        require(checks == row['calls'] and all(benchmark.check(c['input']['command'])['valid'] is c['result_success'] for c in checks),
                'Command-check evidence mismatch')
        loaded = sorted({e['request']['name'] for e in events if e['action'] == 'activate' and e['success']})
        registered = {s['name'] for s in report['packages'][row['arm']]['skills']}
        require(loaded == row['loaded_skills'] and set(loaded) <= registered, 'Skill-read identity mismatch')
        require(row['reference_reads'] == [e['request']['path'] for e in events if e['action'] == 'read' and e['success']],
                'Reference-read count mismatch')
        valid = not list(jsonschema.Draft202012Validator(payload['output_schema']).iter_errors(row['answer']))
        require(row['schema_valid'] is valid and row['completed'] is valid, 'Schema/completion mismatch')
        grades = benchmark.score(fixtures[row['case']], row['answer'], receipts, checks) if valid else None
        require(row['grades'] == grades and row['passed'] is bool(grades and grades['passed']), 'Score changed')
    scores = aggregate(rows)
    comparisons = paired(rows, order)
    supported = scores['pack']['passed'] >= 32 and all(len(c['pack_only']) > len(c['opponent_only']) and c['p_holm'] < .05 for c in comparisons)
    require(report['arms'] == scores and report['paired_comparisons'] == comparisons and
            report['supported_superiority_in_this_experiment'] is supported, 'Aggregate/statistical claim changed')
    field_audit = audit_fields(report, json.loads((benchmark.ROOT / 'evals/query-response-contracts.json').read_text()))
    return {'verified': True, 'current_sources': True, 'collected_all': True, 'arms': scores,
            'paired_comparisons': comparisons, 'supported_superiority_in_this_experiment': supported,
            'query_field_audit': {'arms': field_audit['arms'], 'scope': field_audit['scope']},
            'model_calls': 0, 'cloud_calls': 0,
            'scope': 'Recorded answer/schema/receipt/command checks. Does not attest agent isolation, complete context delivery, native plugin behavior, query semantics or billing.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(json.loads(args.report.read_text())), indent=2))


if __name__ == '__main__':
    main()
