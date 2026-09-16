#!/usr/bin/env python3
"""Report newer changelog BREAKING blocks mentioning shipped CLI path prefixes."""
import argparse
import json
import re
from pathlib import Path
from common import ROOT


def matching_blocks(text, examples, baseline='3.93.0'):
    floor = tuple(map(int, baseline.split('.')))
    prefixes = set()
    for example in examples:
        argv = example['argv']
        end = next((i for i, value in enumerate(argv) if value.startswith('-')), len(argv))
        prefixes.update(' '.join(argv[:n]) for n in range(1, end + 1))
    result = []
    sections = re.split(r'(?m)^(\d+\.\d+\.\d+) - [^\n]+\n', text)
    for index in range(1, len(sections), 2):
        version, body = sections[index:index + 2]
        if tuple(map(int, version.split('.'))) <= floor:
            continue
        for block in re.split(r'\n\s*\n', body):
            if '[BREAKING]' not in block:
                continue
            mentions = sorted(p for p in prefixes if re.search(r'\boci\s+' + re.escape(p) + r'(?:\b|$)', block))
            if mentions:
                result.append({'version': version, 'shipped_prefixes': mentions, 'change': block.strip()})
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('changelog', type=Path)
    parser.add_argument('--baseline', default='3.93.0')
    args = parser.parse_args()
    examples = json.loads((ROOT / 'catalog/examples.json').read_text())['examples']
    matches = matching_blocks(args.changelog.read_text(), examples, args.baseline)
    if matches:
        print(json.dumps({'breaking_changes_mentioning_shipped_prefixes': matches}, indent=2))
