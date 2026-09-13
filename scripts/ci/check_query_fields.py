"""Reject proven query field errors in authored skills and shared references.

Coverage is limited to pinned response contracts and supported JMESPath nodes.
Unsupported commands/expressions are counted explicitly, never certified.
"""
from collections import Counter
import json
from pathlib import Path
import shlex
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/eval'))
from audit_query_fields import inspect_query
from lint_fences import commands
from guard_lib import parse_oci


def scan(paths, contracts):
    counts = Counter()
    findings = []
    for path in paths:
        for line, command in commands(path.read_text()):
            try:
                leaf, options = parse_oci(shlex.split(command, comments=True)[1:])
                if leaf not in contracts or '--query' not in options:
                    counts['outside_contract_coverage'] += 1
                    continue
                result = inspect_query(options['--query'], contracts[leaf]['response'])
                counts[result['status']] += 1
                if result['status'] == 'FAIL':
                    findings.append({'file': str(path.relative_to(ROOT)), 'line': line, 'issues': result['issues']})
            except ValueError:
                counts['unparsed'] += 1
    return {'counts': dict(counts), 'findings': findings, 'ok': not findings}


def main():
    contracts = json.loads((ROOT / 'evals/query-response-contracts.json').read_text())['contracts']
    paths = sorted([*(ROOT / 'skills').rglob('*.md'), *(ROOT / 'references').rglob('*.md')])
    result = scan(paths, contracts)
    print(json.dumps(result, indent=2))
    return int(not result['ok'])


if __name__ == '__main__':
    raise SystemExit(main())
