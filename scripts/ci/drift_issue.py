#!/usr/bin/env python3
"""Prepare a drift notification; publishing requires an explicit flag.

The workflow serializes runs to prevent duplicate creation races. Read failures
must stop publication rather than being interpreted as an empty issue list.
"""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

TITLE = 'CLI required-flag drift'
BODY_LIMIT = 60000


class GitHub:
    def __init__(self, repository):
        self.repository = repository

    def invoke(self, args):
        result = subprocess.run(['gh', *args, '--repo', self.repository],
                                capture_output=True, text=True, timeout=60)
        if result.returncode:
            raise RuntimeError('GitHub request failed; provider output suppressed')
        return result.stdout

    def existing(self):
        rows = json.loads(self.invoke(['issue', 'list', '--state', 'open', '--limit', '1000',
                                      '--search', '"CLI required-flag drift" in:title',
                                      '--json', 'number,title']))
        if not isinstance(rows, list) or len(rows) >= 1000:
            raise ValueError('Incomplete issue discovery')
        if any(not isinstance(r, dict) or not isinstance(r.get('number'), int)
               or not isinstance(r.get('title'), str) for r in rows):
            raise ValueError('Invalid issue discovery')
        return [r['number'] for r in rows if r['title'] == TITLE]

    def create(self, body):
        with tempfile.TemporaryDirectory(prefix='oci-drift-issue-') as directory:
            path = Path(directory) / 'body.md'
            path.write_text(body)
            return self.invoke(['issue', 'create', '--title', TITLE, '--body-file', str(path)]).strip()


def notify(diff, github, *, publish=False, evidence_url=''):
    if not diff.strip():
        return {'status': 'no-drift', 'published': False}
    existing = github.existing()
    if existing:
        return {'status': 'existing', 'issues': existing, 'published': False}
    prefix = ('CLI required flags or shipped-path breaking notes changed. Review the attached diff.\n'
              + (f'Full evidence: {evidence_url}\n' if evidence_url else ''))
    suffix = '\n\nDiff truncated; inspect the full workflow artifact.\n'
    allowance = BODY_LIMIT - len(prefix) - len(suffix)
    body = prefix + diff[:allowance] + (suffix if len(diff) > allowance else '')
    result = {'status': 'would-create', 'published': False, 'body_characters': len(body),
              'diff_truncated': len(diff) > allowance}
    if publish:
        result.update(status='created', published=True, issue=github.create(body))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('diff', type=Path)
    parser.add_argument('--repo', required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--evidence-url', default='')
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    try:
        result = notify(args.diff.read_text(), GitHub(args.repo), publish=args.publish,
                        evidence_url=args.evidence_url)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError):
        result = {'status': 'failed', 'published': False, 'error': 'Drift notification failed'}
    args.report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    return int(result['status'] == 'failed')


if __name__ == '__main__':
    raise SystemExit(main())
