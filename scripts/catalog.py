#!/usr/bin/env python3
"""Bounded catalog queries: output is capped at 400 UTF-8 bytes (at most 400 tokens)."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rows(read_only=False):
    path = ROOT / 'catalog' / ('cli-read.jsonl' if read_only else 'cli.jsonl')
    return [json.loads(line) for line in path.read_text().splitlines()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['find', 'help', 'severity', 'service'])
    parser.add_argument('query', nargs='+')
    parser.add_argument('--service')
    parser.add_argument('--read-only', action='store_true')
    parser.add_argument('--limit', type=int, default=5)
    args = parser.parse_args()
    query = ' '.join(args.query).removeprefix('oci ')
    if args.action == 'service':
        entries = json.loads((ROOT / 'catalog/index.json').read_text())['services']
        output = [json.dumps(r) for r in entries if query in r['name']]
    else:
        entries = rows(args.read_only)
        entries = [r for r in entries if not args.service or r['path'].split()[0] == args.service]
        if args.action == 'find':
            words = [w.rstrip('s') for w in query.lower().split()]
            entries = [r for r in entries if all(w in (r['path'] + ' ' + r['short_help']).lower() for w in words)]
            output = [r['path'] + ' [' + r['kind'] + ']' for r in entries]
        else:
            entries = [r for r in entries if r['path'] == query]
            output = [json.dumps({k: r[k] for k in (('path', 'kind', 'severity') if args.action == 'severity' else ('path', 'required', 'short_help'))}) for r in entries]
    text = '\n'.join(output[:max(1, min(args.limit, 20))]) or 'No matching catalog entry.'
    data = text.encode('utf-8')
    print(data[:380].decode('utf-8', errors='ignore') + ('\n[output capped]' if len(data) > 380 else ''))


if __name__ == '__main__':
    main()
