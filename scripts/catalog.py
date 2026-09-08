#!/usr/bin/env python3
"""Bounded catalog queries; output is at most 400 UTF-8 bytes including its newline."""
import argparse
import difflib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rows(read_only=False):
    path = ROOT / 'catalog' / ('cli-read.jsonl' if read_only else 'cli.jsonl')
    return [json.loads(line) for line in path.read_text().splitlines()]


def bounded_json(items, *, ok=True):
    result = {'ok': ok, 'items': items, 'truncated': False}
    def dump():
        return json.dumps(result, ensure_ascii=True, separators=(',', ':'))
    while len(dump().encode()) > 399:
        result['truncated'] = True
        if len(result['items']) > 1:
            result['items'].pop()
        elif result['items'] and isinstance(result['items'][0], dict):
            row = result['items'][0]
            candidates = [(len(str(value)), key) for key, value in row.items() if key != 'path']
            if candidates:
                del row[max(candidates)[1]]
            else:
                result['items'] = []
        else:
            result['items'] = []
    return dump()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['find', 'help', 'required', 'severity', 'service', 'query'])
    parser.add_argument('query', nargs='*')
    parser.add_argument('--service')
    parser.add_argument('--skill')
    parser.add_argument('--product')
    parser.add_argument('--fields')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--read-only', action='store_true')
    parser.add_argument('--limit', type=int, default=5)
    args = parser.parse_args()
    query = ' '.join(args.query).removeprefix('oci ')
    if not query and args.action != 'query':
        parser.error('query text is required')
    all_rows = rows(args.read_only)
    selected = [r for r in all_rows if not args.service or r['path'].split()[0] == args.service]
    if args.action == 'service' or args.action == 'query' and not args.skill:
        entries = json.loads((ROOT / 'catalog/index.json').read_text())['services']
        wanted = args.service or args.product or query
        if not wanted:
            parser.error('query requires --service, --skill, or --product')
        entries = [r for r in entries if wanted.lower() in (r['name'] + ' ' + r['purpose']).lower()]
        fields = (args.fields or 'name,ops,read_only,purpose').split(',')
    elif args.action == 'query':
        examples = json.loads((ROOT / 'catalog/examples.json').read_text())['examples']
        services = {row['argv'][0] for row in examples if row['skill'] == args.skill}
        entries = [r for r in selected if r['path'].split()[0] in services]
        fields = (args.fields or 'path,kind').split(',')
    elif args.action == 'find':
        words = [w.rstrip('s') for w in query.lower().split()]
        entries = [r for r in selected if all(w in (r['path'] + ' ' + r['short_help']).lower() for w in words)]
        fields = ['path', 'kind']
    else:
        entries = [r for r in selected if r['path'] == query]
        fields = {'severity': ['path', 'kind', 'severity', 'has_force', 'has_dry_run'],
                  'required': ['path', 'required'], 'help': ['path', 'required', 'short_help']}[args.action]
    ok = bool(entries)
    output = [{k: r[k] for k in fields if k in r} for r in entries[:max(1, min(args.limit, 20))]]
    if not ok:
        output = [{'suggestions': difflib.get_close_matches(query, [r['path'] for r in all_rows], n=3)}]
    if args.json:
        print(bounded_json(output, ok=ok))
    else:
        text = '\n'.join(json.dumps(row, ensure_ascii=True) for row in output)
        if not ok:
            text = 'No matching catalog entry.\n' + text
        data = text.encode()
        print(data[:380].decode('utf-8', errors='ignore') + ('\n[output capped]' if len(data) > 380 else ''))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
