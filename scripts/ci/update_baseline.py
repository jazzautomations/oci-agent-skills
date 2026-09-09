#!/usr/bin/env python3
"""Explicitly snapshot content debt; CI never regenerates this baseline automatically."""
import json
import subprocess
import sys
from common import ROOT

if __name__ == '__main__':
    result = {}
    for name in ('frontmatter', 'refs', 'portable', 'budget', 'licenses'):
        process = subprocess.run([sys.executable, str(ROOT / 'scripts/ci' / ('check_' + name + '.py'))], text=True, capture_output=True)
        report = json.loads(process.stdout)
        result[name] = report['findings']
    (ROOT / 'catalog/validation-baseline.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: len(value) for key, value in result.items()}, sort_keys=True))
