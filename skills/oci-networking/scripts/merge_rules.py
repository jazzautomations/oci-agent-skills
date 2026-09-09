#!/usr/bin/env python3
"""Merge complete local rule arrays for review; no OCI mutation or calls."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts'))
from lib import oci_ro  # OCI calls, if added, must use this wrapper.

def merge(current, additions):
    if not isinstance(current, list) or not isinstance(additions, list):
        raise ValueError('Expected two JSON arrays')
    result, seen = [], set()
    for rule in current + additions:
        if not isinstance(rule, dict):
            raise ValueError('Each rule must be an object')
        key = json.dumps(rule, sort_keys=True, separators=(',', ':'))
        if key not in seen:
            seen.add(key)
            result.append(rule)
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('current', type=Path)
    parser.add_argument('additions', type=Path)
    args = parser.parse_args()
    try:
        result = merge(json.loads(args.current.read_text()), json.loads(args.additions.read_text()))
    except (OSError, ValueError):
        parser.exit(2, 'Invalid local rule arrays; no output produced.\n')
    print(json.dumps(result, ensure_ascii=True, indent=2))

if __name__ == '__main__':
    main()
