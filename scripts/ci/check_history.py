#!/usr/bin/env python3
"""Scan reachable Git patch bodies; print counts and blob locations, never matches."""
import json
import re
import subprocess
from check_no_secrets import PATTERNS
from common import ROOT

HISTORY_PATTERNS = {
    **PATTERNS,
    'email': r'\b[A-Za-z0-9.!#$%&\x27*+/=?^_`{|}~-]+@(?!example\.(?:com|net|org|invalid)\b)[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+\b',
    'private_key': r'-----BEGIN (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----',
}
HUNK = re.compile(r'^@@ -\d+(?:,(\d+))? \+\d+(?:,(\d+))? @@')


def patch_lines(history):
    """Yield hunk content only, using line counts to distinguish body from headers.

    Commit identities, messages and their Co-Authored-By/Claude-Session trailers
    are outside this scope. Identical text added to a file is still body content.
    """
    commit = old_blob = new_blob = old_path = new_path = None
    in_diff = False
    old_left = new_left = 0
    for line in history.splitlines():
        if old_left or new_left:
            prefix = line[:1]
            if prefix == '\\':
                continue  # Git's no-newline marker is not file content.
            if prefix in {'+', '-', ' '}:
                old_left -= int(prefix in {'-', ' '})
                new_left -= int(prefix in {'+', ' '})
                yield {'commit': commit, 'side': {'+':'added', '-':'removed', ' ':'context'}[prefix],
                       'file': old_path if prefix == '-' else new_path,
                       'blob': old_blob if prefix == '-' else new_blob, 'body': line[1:]}
                continue
            old_left = new_left = 0
        if line.startswith('commit '):
            commit = line.split()[1]
            in_diff = False
        elif line.startswith('diff --git '):
            in_diff = True
            old_blob = new_blob = old_path = new_path = None
        elif in_diff:
            if line.startswith('index '):
                match = re.match(r'index ([0-9a-f]+)\.\.([0-9a-f]+)', line)
                if match:
                    old_blob, new_blob = match.groups()
            elif line.startswith(('--- ', '+++ ')):
                path = line[4:]
                if path.startswith('"'):
                    try:
                        path = json.loads(path)
                    except ValueError:
                        path = '<quoted path>'
                path = path[2:] if path.startswith(('a/', 'b/')) else path
                if line.startswith('--- '):
                    old_path = path
                else:
                    new_path = path
            else:
                match = HUNK.match(line)
                if match:
                    old_left, new_left = (int(n) if n is not None else 1 for n in match.groups())


def inspect(history):
    counts = dict.fromkeys(HISTORY_PATTERNS, 0)
    locations = {}
    for entry in patch_lines(history):
        matched = {name: len(re.findall(pattern, entry['body'])) for name, pattern in HISTORY_PATTERNS.items()}
        for name, count in matched.items():
            counts[name] += count
        if not any(matched.values()):
            continue
        key = tuple(entry[k] for k in ('commit', 'file', 'blob', 'side'))
        safe_location = {k:v for k,v in entry.items() if k != 'body'}
        if safe_location['file']:
            for pattern in HISTORY_PATTERNS.values():
                safe_location['file'] = re.sub(pattern, '<redacted>', safe_location['file'])
        location = locations.setdefault(key, safe_location)
        detail = location.setdefault('counts', {})
        for name, count in matched.items():
            if count:
                detail[name] = detail.get(name, 0) + count
    return counts, list(locations.values())


def scan(history):
    return inspect(history)[0]


def main():
    history = subprocess.check_output([
        'git', 'log', '--all', '--root', '-m', '--format=commit %H', '--patch',
        '--unified=0', '--full-index', '--no-ext-diff', '--no-textconv', '--no-color',
    ], cwd=ROOT).decode('utf-8', errors='replace')
    counts, locations = inspect(history)
    print(json.dumps({'scope':'All reachable textual patch bodies, including additions and deletions and separate merge-parent diffs. Commit author/committer identities, messages and Co-Authored-By/Claude-Session trailers are excluded. Reserved example domains excluded; binary content and arbitrary tenancy/display names are not inferred.',
                      'counts':counts, 'locations':locations, 'ok':not any(counts.values()),
                      'owner':None if not any(counts.values()) else 'repository history owner'}, sort_keys=True))
    return int(any(counts.values()))


if __name__ == '__main__':
    raise SystemExit(main())
