#!/usr/bin/env python3
"""Extract or byte-check the plan stencil, applying the overriding B3/N3 errata."""
import argparse
from pathlib import Path
from common import ROOT


def expected(plan):
    section = plan.split('### 4.1 ', 1)[1].split('### 4.2 ', 1)[0]
    template = section.split('````markdown\n', 1)[1].split('\n````', 1)[0] + '\n'
    return template.replace('research/data/error-corpus.json', 'references/error-corpus.json').replace('verified: "live" | "shape-only"', 'verified: "live" | "partial" | "shape-only"')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=ROOT / 'research/00-PLAN-V2.1.md')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    content = expected(args.plan.read_text())
    target = ROOT / 'skills/_TEMPLATE/SKILL.md.template'
    if args.write:
        target.write_text(content)
    elif target.read_bytes() != content.encode():
        raise SystemExit('Template differs from plan plus B3/N3 errata')
    print('Template matches plan plus B3/N3 errata.')
