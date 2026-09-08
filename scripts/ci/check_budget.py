#!/usr/bin/env python3
"""Enforce source budgets using characters / 4, rounded up: an estimate, not tokens."""
import json
import sys
import yaml
from common import ROOT, arguments, files, finding, finish

CAPS = {'untrusted-output.md': 400, 'operator-contract.md': 1200, 'error-triage.md': 1600,
        'redaction.md': 500, 'cross-service-pitfalls.md': 1400, 'auth-modes.md': 1600,
        'jmespath.md': 1200, 'iam-variables.md': 2000, 'console-links.md': 1200,
        'realms-endpoints.md': 1400, 'architecture-center.md': 1800,
        'windows-powershell.md': 900, 'oci-doc-urls.md': 1000}


def validate(path):
    if '_TEMPLATE' in path.parts or path.suffix != '.md':
        return []
    text = path.read_text()
    if path.name == 'SKILL.md':
        parts = text.split('---', 2)
        text = parts[2] if len(parts) == 3 else text
        cap = 1500
    elif 'references' in path.parts:
        cap = CAPS.get(path.name, 2000)
    else:
        return []
    result = []
    if (len(text) + 3) // 4 > cap:
        result.append(finding(path, 1, 'body_budget_estimate'))
    if path.name == 'SKILL.md' and len(path.read_text().splitlines()) > 200:
        result.append(finding(path, 1, 'skill_line_budget'))
    return result


def main():
    args = arguments(__doc__)
    selected = files(args.paths or [ROOT / 'skills', ROOT / 'references'])
    findings = [f for p in selected for f in validate(p)]
    mass = 0
    for path in selected:
        if path.name == 'SKILL.md' and '_TEMPLATE' not in path.parts:
            try:
                mass += len(yaml.safe_load(path.read_text().split('---', 2)[1]).get('description', ''))
            except (IndexError, TypeError, AttributeError, yaml.YAMLError):
                findings.append(finding(path, 1, 'invalid_yaml'))
    if mass > 13200:
        findings.append(finding(ROOT / 'skills', 1, 'description_mass'))
    if not args.paths:
        import asyncio
        sys.path.insert(0, str(ROOT / 'runtime'))
        from oci_readonly.server import mcp
        schemas = asyncio.run(mcp.list_tools())
        size = len(json.dumps([t.model_dump(exclude_none=True) for t in schemas], separators=(',', ':')))
        if (size + 3) // 4 > 3500:
            findings.append(finding(ROOT / 'runtime', 1, 'schema_budget_estimate'))
    return finish('budget', findings, args, len(selected))


if __name__ == '__main__':
    raise SystemExit(main())
