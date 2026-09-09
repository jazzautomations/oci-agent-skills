#!/usr/bin/env python3
"""Render installed Click leaves as path TAB sorted required flags, without callbacks."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from inventory import cli_inventory

if __name__ == '__main__':
    for row in cli_inventory()['commands']:
        print(row['path'] + '\t' + ' '.join(sorted(row['required'])))
