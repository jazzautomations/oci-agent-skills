import json
from pathlib import Path
import sys

import jmespath
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/eval'))
from audit_query_fields import audit, inspect_query

CONTRACTS = json.loads((ROOT / 'evals/query-response-contracts.json').read_text())


@pytest.mark.parametrize('bad_path,bad_query,path,query,payload,expected', [
    ('os bucket list', 'data[]."public-access-type"', 'os bucket get', 'data."public-access-type"',
     {'data': {'name': 'assets', 'public-access-type': 'ObjectRead'}}, 'ObjectRead'),
    ('os bucket get', 'data."lifecycle-policy"', 'os object-lifecycle-policy get', 'data.items',
     {'data': {'items': [{'name': 'archive', 'action': 'ARCHIVE'}]}}, [{'name': 'archive', 'action': 'ARCHIVE'}]),
    ('monitoring alarm list', 'data[].{enabled:enabled}', 'monitoring alarm list', 'data[].{enabled:"is-enabled"}',
     {'data': [{'is-enabled': False}]}, [{'enabled': False}]),
    ('ce node-pool list', 'data[].{size:"node-config-details.size"}', 'ce node-pool list', 'data[].{size:"node-config-details".size}',
     {'data': [{'node-config-details': {'size': 3}}]}, [{'size': 3}]),
    ('cloud-guard problem list', 'data[].{risk:risk}', 'cloud-guard problem list', 'data.items[].{risk:"risk-level"}',
     {'data': {'items': [{'risk-level': 'CRITICAL'}]}}, [{'risk': 'CRITICAL'}]),
    ('os object list', 'data.objects', 'os object list', '{items:data[].name,next:"next-start-with"}',
     {'data': [{'name': 'a'}, {'name': 'b'}], 'prefixes': [], 'next-start-with': 'c'}, {'items': ['a', 'b'], 'next': 'c'}),
])
def test_response_field_repairs(bad_path, bad_query, path, query, payload, expected):
    assert inspect_query(bad_query, CONTRACTS['contracts'][bad_path]['response'])['status'] == 'FAIL'
    assert inspect_query(query, CONTRACTS['contracts'][path]['response'])['status'] == 'PASS'
    assert jmespath.search(query, payload) == expected
    if path == bad_path:
        assert jmespath.search(bad_query, payload) != expected


@pytest.mark.parametrize('query,schema', [
    ('data.foo', {}),
    ('data.foo', {'type': 'object', 'properties': {'data': {'type': 'object', 'properties': {}, 'additionalProperties': {}}}}),
    ('data[?enabled]', CONTRACTS['contracts']['monitoring alarm list']['response']),
    ('length(data)', CONTRACTS['contracts']['monitoring alarm list']['response']),
])
def test_unknown_or_unsupported_shapes_are_not_certified(query, schema):
    assert inspect_query(query, schema)['status'] == 'UNVERIFIED'


def test_malformed_query_is_a_failure():
    assert inspect_query('data[', {})['status'] == 'FAIL'


def test_unrelated_fields_are_not_required_but_invalid_access_fails():
    schema = CONTRACTS['contracts']['ce node-pool list']['response']
    assert inspect_query('data[].name', schema)['status'] == 'PASS'
    assert inspect_query('data[].name.size', schema)['status'] == 'FAIL'


def test_audit_keeps_empty_commands_and_missing_contracts_explicit():
    report = {'results': [
        {'arm': 'pack', 'case': 'A', 'answer': {'commands': ['oci monitoring alarm list --query data']}},
        {'arm': 'pack', 'case': 'B', 'answer': {'commands': ['oci monitoring alarm list --query "data[].enabled"']}},
        {'arm': 'pack', 'case': 'C', 'answer': {'commands': []}},
        {'arm': 'pack', 'case': 'D', 'answer': {'commands': ['oci fake read --query data']}},
        {'arm': 'pack', 'case': 'E', 'answer': {'commands': ['oci fake read --query "data["']}},
    ]}
    result = audit(report, CONTRACTS)
    assert result['arms']['pack'] == {'commands': 4, 'field_status': {'PASS': 1, 'FAIL': 2, 'UNVERIFIED': 1},
                                       'cases_with_field_errors': ['B', 'E'], 'cases_without_commands': ['C']}
    assert result['model_calls'] == result['cloud_calls'] == 0


def test_array_flatten_preserves_nested_element_schema():
    schema = {'type': 'array', 'items': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}}}}}
    assert inspect_query('[].name', schema)['status'] == 'PASS'
