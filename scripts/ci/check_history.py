#!/usr/bin/env python3
"""Scan Git patch history for credential-shaped patterns without printing matched data."""
import json
import re
import subprocess
from check_no_secrets import PATTERNS
from common import ROOT

if __name__ == '__main__':
    history = subprocess.check_output(['git', 'log', '--format=', '--patch', '--no-ext-diff'], cwd=ROOT).decode('utf-8', errors='replace')
    counts = {name: len(re.findall(pattern, history)) for name, pattern in PATTERNS.items()}
    print(json.dumps({'scope': 'git patch history, heuristic patterns only', 'counts': counts, 'ok': not any(counts.values())}, sort_keys=True))
    raise SystemExit(int(any(counts.values())))
