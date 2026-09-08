#!/usr/bin/env python3
"""Reproduce foundation catalog counts and the OCI-only guard confusion matrix offline."""
import argparse
import json
from collections import Counter
from catalog import ROOT, rows
from guard_lib import classify_leaf


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unowned-services', action='store_true')
    args = parser.parse_args()
    data = rows()
    index = json.loads((ROOT / 'catalog/index.json').read_text())
    unowned = [r['name'] for r in index['services'] if r['read_only'] == 0]
    if args.unowned_services:
        print('\n'.join(unowned))
        return
    matrix = Counter((r['kind'], classify_leaf(r['path'])) for r in data)
    baseline = json.loads((ROOT / 'catalog/validation-baseline.json').read_text())
    print(json.dumps({'cli_version': index['cli_version'], 'leaf_count': len(data),
        'service_count': len(index['services']), 'read_allowlist_count': len(rows(True)),
        'inventory_labels': dict(sorted(Counter(r['kind'] for r in data).items())),
        'oci_leaf_matrix': {'/'.join(k): v for k, v in sorted(matrix.items())},
        'critical_denied': sum(r['severity'] == 'CRITICAL' and classify_leaf(r['path']) == 'deny' for r in data),
        'critical_total': sum(r['severity'] == 'CRITICAL' for r in data),
        'legacy_validation_findings': {k: len(v) for k, v in baseline.items()},
        'unowned_services': unowned}, indent=2))


if __name__ == '__main__':
    main()
