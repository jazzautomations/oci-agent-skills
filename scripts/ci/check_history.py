#!/usr/bin/env python3
"""Scan all reachable Git patch bodies and metadata; print counts, never matches."""
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


def scan(history):
    return {name: len(re.findall(pattern, history)) for name, pattern in HISTORY_PATTERNS.items()}


def main():
    history = subprocess.check_output(['git','log','--all','--format=fuller','--patch','--no-ext-diff'],cwd=ROOT).decode('utf-8',errors='replace')
    counts = scan(history)
    print(json.dumps({'scope':'All reachable commit metadata and patch bodies; heuristic identifiers, email addresses and key blocks. Reserved example domains excluded; arbitrary tenancy/display names cannot be inferred.',
                      'counts':counts,'ok':not any(counts.values()),'owner':None if not any(counts.values()) else 'repository history owner'},sort_keys=True))
    return int(any(counts.values()))


if __name__ == '__main__':
    raise SystemExit(main())
