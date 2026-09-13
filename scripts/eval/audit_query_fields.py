"""Audit recorded JMESPath field access against pinned OCI response contracts.

This is an offline field/type check, not execution or end-to-end task scoring.
Unknown contracts, dynamic objects and unsupported expressions stay unverified.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shlex
import sys

import jmespath

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from guard_lib import parse_oci


def inspect_query(query, schema):
    issues = []
    unknown = []

    def walk(node, current):
        kind = node['type']
        children = node.get('children', [])
        if kind == 'identity':
            return current
        if kind == 'field':
            field = node['value']
            if not current:
                unknown.append('Unknown shape at field ' + field)
                return {}
            if current.get('type') != 'object':
                issues.append('Field ' + field + ' accessed on ' + str(current.get('type')))
                return {}
            if field in current.get('properties', {}):
                return current['properties'][field]
            if current.get('additionalProperties', True) is False:
                issues.append('Field absent from response model: ' + field)
            else:
                unknown.append('Dynamic field: ' + field)
            return {}
        if kind == 'subexpression':
            for child in children:
                current = walk(child, current)
            return current
        if kind == 'flatten':
            value = walk(children[0], current)
            if not value:
                unknown.append('Unknown flatten input')
                return {}
            if value.get('type') != 'array':
                issues.append('Flatten expects an array, got ' + str(value.get('type')))
                return {}
            item = value.get('items', {})
            return item if item.get('type') == 'array' else value
        if kind == 'projection':
            value = walk(children[0], current)
            if not value:
                unknown.append('Unknown projection input')
                return {}
            if value.get('type') != 'array':
                issues.append('Projection expects an array, got ' + str(value.get('type')))
                return {}
            return {'type': 'array', 'items': walk(children[1], value.get('items', {}))}
        if kind == 'multi_select_dict':
            return {'type': 'object', 'properties': {
                child['value']: walk(child['children'][0], current) for child in children}}
        unknown.append('Unsupported expression: ' + kind)
        return {}

    try:
        tree = jmespath.parser.Parser().parse(query).parsed
        output = walk(tree, schema)
    except jmespath.exceptions.JMESPathError as exc:
        return {'status': 'FAIL', 'issues': ['Invalid JMESPath: ' + type(exc).__name__],
                'unverified': [], 'output_schema': {}}
    return {'status': 'FAIL' if issues else 'UNVERIFIED' if unknown else 'PASS',
            'issues': sorted(set(issues)), 'unverified': sorted(set(unknown)), 'output_schema': output}


def audit(report, contracts):
    rows = []
    for row in report['results']:
        for index, command in enumerate(row['answer']['commands']):
            result = {'arm': row['arm'], 'case': row['case'], 'command_index': index,
                      'command_sha256': hashlib.sha256(command.encode()).hexdigest()}
            try:
                argv = shlex.split(command)
                if not argv or argv[0] != 'oci':
                    raise ValueError('Not an OCI proposal')
                path, options = parse_oci(argv[1:])
                query = options.get('--query')
                if not isinstance(query, str):
                    raise ValueError('Missing query')
                result.update(path=path, query=query)
                contract = contracts['contracts'].get(path)
                result.update(inspect_query(query, contract['response'] if contract else {}))
                if not contract and result['status'] != 'FAIL':
                    result.update(status='UNVERIFIED', unverified=['No pinned response contract'])
            except (ValueError, TypeError):
                result.update(status='FAIL', issues=['Unparseable OCI/query proposal'], unverified=[])
            rows.append(result)
    arms = sorted({r['arm'] for r in report['results']})
    return {'format_version': 1, 'scope': 'Every recorded command query inspected for response field access. PASS means known fields/types only; it does not prove scope, filtering, pagination, joins, service query languages, command sequence completeness or task correctness.',
            'model_calls': 0, 'cloud_calls': 0, 'rows': rows,
            'arms': {arm: {'commands': sum(r['arm'] == arm for r in rows),
                           'field_status': dict(Counter(r['status'] for r in rows if r['arm'] == arm)),
                           'cases_with_field_errors': sorted({r['case'] for r in rows if r['arm'] == arm and r['status'] == 'FAIL'}),
                           'cases_without_commands': sorted(r['case'] for r in report['results'] if r['arm'] == arm and not r['answer']['commands'])}
                     for arm in arms}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('--contracts', type=Path, default=ROOT / 'evals/query-response-contracts.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = audit(json.loads(args.report.read_text()), json.loads(args.contracts.read_text()))
    result['report_sha256'] = hashlib.sha256(args.report.read_bytes()).hexdigest()
    result['contracts_sha256'] = hashlib.sha256(args.contracts.read_bytes()).hexdigest()
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result['arms'], indent=2))
    return int(any(r['status'] != 'PASS' for r in result['rows']))


if __name__ == '__main__':
    raise SystemExit(main())
