#!/usr/bin/env python3
'''Run the ordered incident sweep as reads only and print counts, never raw values.'''
import argparse
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts'))
from lib.oci_ro import run
from lib.sanitize import emit

NAME = re.compile(r'^[A-Za-z0-9._-]{1,120}$')
STAMP = '%Y-%m-%dT%H:%M:%SZ'


def label(value):
    return value if isinstance(value, str) and NAME.match(value) else 'unparsed'


def tally(rows, key):
    counts = {}
    for row in rows if isinstance(rows, list) else []:
        name = label(row.get(key) if isinstance(row, dict) else None)
        counts[name] = counts.get(name, 0) + 1
    return counts


def step(number, name, argv, scope):
    result = run(argv, profile=scope['profile'], region=scope['region'], sanitize=False)
    if not result['ok']:
        return {'step': number, 'name': name, 'ok': False, 'error': result['error']}
    rows = result['data']
    rows = rows if isinstance(rows, list) else ([] if rows is None else [rows])
    return {'step': number, 'name': name, 'ok': True, 'rows': len(rows),
            'truncated': result['truncated']}


def sweep(scope):
    compartment, start, end = scope['compartment'], scope['start'], scope['end']
    steps = [
        (1, 'alarms', ['monitoring', 'alarm-status', 'list-alarms-status',
                       '--compartment-id', compartment, '--limit', '50',
                       '--query', 'data[?status!=`OK`].{a:"display-name",s:status}']),
        (3, 'cloud-guard', ['cloud-guard', 'problem', 'list', '--compartment-id', compartment,
                            '--lifecycle-detail', 'OPEN', '--risk-level', 'CRITICAL',
                            '--limit', '20', '--query', 'data.items[].{r:"resource-name"}']),
        (4, 'namespaces', ['monitoring', 'metric', 'list', '--compartment-id', compartment,
                           '--limit', '200', '--query', 'data[].{k:namespace}']),
        (5, 'log-errors', ['logging-search', 'search-logs', '--search-query',
                           'search "%s" | where "data.level" = \'ERROR\'' % compartment,
                           '--time-start', start, '--time-end', end, '--limit', '100',
                           '--query', 'data.results[].data.datetime']),
        (7, 'maintenance', ['compute', 'instance-maintenance-event', 'list',
                            '--compartment-id', compartment, '--limit', '20',
                            '--query', 'data[].{s:"lifecycle-state"}']),
        (8, 'work-requests', ['work-requests', 'work-request', 'list',
                              '--compartment-id', compartment, '--limit', '50',
                              '--query', 'data[?status!=`SUCCEEDED`].{k:"operation-type"}']),
    ]
    steps.extend([
        (6, 'instance', ['compute', 'instance', 'get', '--instance-id', scope['instance'],
                         '--query', 'data.{s:"lifecycle-state",shape:shape}']),
        (9, 'limits', ['limits', 'value', 'list', '--compartment-id', scope['tenancy'],
                       '--service-name', 'compute', '--limit', '200',
                       '--query', 'data[?value==`0`].{name:name}']),
        (10, 'support', ['support', 'incident', 'list', '--compartment-id', scope['tenancy'],
                         '--limit', '20', '--query', 'data.items[].{s:status}']),
    ])
    steps.append((2, 'audit', []))
    report = []
    for number, name, argv in sorted(steps):
        if number != 2:
            report.append(step(number, name, argv, scope))
            continue
        audit = run(['audit', 'event', 'list', '--compartment-id', compartment,
                     '--start-time', start, '--end-time', end, '--query',
                     'data[].{k:"event-type",method:data.request.action}'],
                    profile=scope['profile'], region=scope['region'], sanitize=False)
        entry = {'step': 2, 'name': 'audit', 'ok': audit['ok']}
        if audit['ok']:
            rows = audit['data'] or []
            candidates = [row for row in rows if mutation_candidate(row)]
            entry.update(rows=len(rows), mutation_candidates=tally(candidates, 'k'),
                         page_bounded=True, note='write attempts, not confirmed changes')
        else:
            entry['error'] = audit['error']
        report.append(entry)
    return report


def mutation_candidate(row):
    """Exclude read methods and read-shaped operations, including POST-based lists."""
    if not isinstance(row, dict):
        return False
    method = str(row.get('method', '')).upper()
    event = str(row.get('k', ''))
    if method not in {'POST', 'PUT', 'PATCH', 'DELETE'}:
        return False
    return not re.search(r'(?:^|\.)(?:List|Get|Head|Search|Summarize|Query)', event, re.I)


def main():
    parser = argparse.ArgumentParser(description=__doc__, epilog='Required env: PROFILE REGION COMPARTMENT_ID TENANCY_ID INSTANCE_ID; optional WINDOW_HOURS (1–24, default 3). Ten reads in order; JSON output is unconditional.')
    parser.add_argument('--json', action='store_true', help='Emit JSON (default)')
    parser.parse_args()
    required = ('PROFILE', 'REGION', 'COMPARTMENT_ID', 'TENANCY_ID', 'INSTANCE_ID')
    if not all(os.environ.get(key) for key in required):
        parser.error('Set ' + ', '.join(required) + '; optional WINDOW_HOURS (default 3)')
    try:
        hours = int(os.environ.get('WINDOW_HOURS', '3'))
        if not 1 <= hours <= 24:
            raise ValueError('WINDOW_HOURS must be 1-24')
    except ValueError as exc:
        print(emit({'ok': False, 'kind': 'invalid_window', 'detail': str(exc)}))
        return 1
    end = datetime.now(timezone.utc)
    scope = {'profile': os.environ['PROFILE'], 'region': os.environ['REGION'],
             'compartment': os.environ['COMPARTMENT_ID'],
             'tenancy': os.environ['TENANCY_ID'], 'instance': os.environ['INSTANCE_ID'],
             'start': (end - timedelta(hours=hours)).strftime(STAMP),
             'end': end.strftime(STAMP)}
    report = sweep(scope)
    print(emit({'ok': all(entry['ok'] for entry in report), 'window_hours': hours, 'start': scope['start'],
                'end': scope['end'], 'steps': report, 'created': False,
                'note': 'counts only; empty means this identity saw nothing, not absence'}))
    return 0 if all(entry['ok'] for entry in report) else 1


if __name__ == '__main__':
    raise SystemExit(main())
