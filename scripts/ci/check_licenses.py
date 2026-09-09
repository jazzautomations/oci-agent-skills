#!/usr/bin/env python3
"""Check root Apache-2.0, skill LICENSE.txt, and any vendored pricing UPL notice."""
from common import ROOT, arguments, finding, finish


def validate(root):
    result = []
    license = root / 'LICENSE'
    if not license.is_file() or 'Apache License' not in license.read_text() or 'Version 2.0' not in license.read_text():
        result.append(finding(license, 1, 'root_apache_license'))
    for skill in sorted((root / 'skills').glob('*/SKILL.md')):
        if skill.parent.name == '_TEMPLATE':
            continue
        license = skill.parent / 'LICENSE.txt'
        if not license.is_file() or not license.read_text().strip():
            result.append(finding(license, 1, 'missing_skill_license'))
    for vendor in (root / 'vendor').glob('*pric*'):
        texts = '\n'.join(p.read_text(errors='replace') for p in vendor.rglob('*') if p.is_file() and ('LICENSE' in p.name.upper() or 'NOTICE' in p.name.upper()))
        if 'Universal Permissive License' not in texts or 'Copyright' not in texts:
            result.append(finding(vendor, 1, 'missing_upl_notice'))
    return result


if __name__ == '__main__':
    args = arguments(__doc__)
    roots = args.paths or [ROOT]
    raise SystemExit(finish('licenses', [f for root in roots for f in validate(root)], args, len(roots)))
