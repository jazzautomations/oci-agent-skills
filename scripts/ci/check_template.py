#!/usr/bin/env python3
"""Verify the pinned stencil without private research; optionally regenerate from a plan."""
import argparse
import hashlib
import json
from pathlib import Path
from common import ROOT


def expected(plan):
    section = plan.split('### 4.1 ', 1)[1].split('### 4.2 ', 1)[0]
    template = section.split('````markdown\n', 1)[1].split('\n````', 1)[0] + '\n'
    return template.replace('research/data/error-corpus.json', 'references/error-corpus.json').replace('verified: "live" | "shape-only"', 'verified: "live" | "partial" | "shape-only"')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, help='Optional authoring plan; not required in a clone')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    target = ROOT / 'skills/_TEMPLATE/SKILL.md.template'
    provenance = ROOT / 'scripts/ci/template-source.json'
    if args.write and not args.plan:
        parser.error('--write requires an explicit --plan')
    if args.write:
        content = expected(args.plan.read_text())
        target.write_text(content)
        record = json.loads(provenance.read_text())
        record.update(source=args.plan.name,
                      source_sha256=hashlib.sha256(args.plan.read_bytes()).hexdigest(),
                      template_sha256=hashlib.sha256(content.encode()).hexdigest())
        provenance.write_text(json.dumps(record, indent=2) + '\n')
    else:
        record = json.loads(provenance.read_text())
        if hashlib.sha256(target.read_bytes()).hexdigest() != record['template_sha256']:
            raise SystemExit('Template differs from the pinned plan-derived stencil')
        if args.plan and target.read_bytes() != expected(args.plan.read_text()).encode():
            raise SystemExit('Template differs from supplied plan plus B3/N3 errata')
    print('Template matches the pinned plan-derived stencil (B3/N3 errata).')
