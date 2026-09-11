import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from read_contract import check, describe


def test_metadata_covers_only_current_read_leaves():
    rows = [json.loads(line) for line in (ROOT / 'catalog/cli.jsonl').read_text().splitlines()]
    data = json.loads((ROOT / 'catalog/read-contracts.json').read_text())
    assert set(data['commands']) == {r['path'] for r in rows if r['read_only']}


def test_contract_exposes_alias_and_pagination_without_credentials():
    data = describe('compute instance list')
    assert data['ok'] and data['has_limit']
    assert describe('iam policy list')['aliases']['-c'] == '--compartment-id'
    assert '--compartment-id' in data['required']
    assert '--limit' not in describe('audit event list')['flags']


def test_valid_alias_and_case_insensitive_enum():
    assert check('oci iam policy list -c "$C" --limit 20 --query data')['valid']
    assert check('oci compute instance list --compartment-id "$C" --limit 20 --lifecycle-state running --query \'data[].shape\'')['valid']


@pytest.mark.parametrize('command,code', [
    ('oci iam compartment list --limit 20 --query data', 'missing_required_options'),
    ('oci iam policy list -c "$C" --all --limit 20 --query data', 'unbounded_pagination'),
    ('oci compute instance list-vnics --instance-id "$I" --query data', 'missing_bounded_limit'),
    ('oci audit event list -c "$C" --start-time "$FROM" --end-time "$TO" --limit 20 --query data', 'unknown_option_or_invalid_syntax'),
    ('oci compute instance list --compartment-id "$C" --limit 0 --query data', 'invalid_page_bound'),
    ('oci compute instance list --compartment-id "$C" --limit 20 --query "data["', 'invalid_jmespath'),
    ('oci compute instance list --compartment-id "$C" --limit 20 --lifecycle-state invented --query data', 'invalid_choice'),
    ('oci iam policy list -c "$C" --compartment-id "$C" --limit 20 --query data', 'duplicate_alias'),
    ('oci compute instance list -c "$C" --limit 20 --query data | wc', 'shell_composition'),
    ('oci iam region list --query "`literal`"', 'shell_composition'),
])
def test_invalid_proposals_are_not_executed(command, code, monkeypatch):
    import subprocess
    monkeypatch.setattr(subprocess, 'run', lambda *a, **k: pytest.fail('Must never execute a command'))
    result = check(command)
    assert not result['valid']
    assert code in {issue['code'] for issue in result['issues']}


def test_diagnostics_do_not_echo_argument_values():
    value = 'synthetic-private-argument-value'
    result = check(f'oci compute instance list -c "{value}" --invalid-option "{value}"')
    assert value not in json.dumps(result)


@pytest.mark.parametrize('value', [None, '', 'x' * 16385])
def test_invalid_input_size_is_bounded(value):
    assert check(value)['issues'] == [{'code': 'command_size'}]


def test_unknown_leaf_and_mutations_have_no_contract():
    assert not describe('no such service')['ok']
    assert not describe('compute instance terminate')['ok']
    assert not check('oci compute instance terminate --instance-id "$I" --query data')['valid']


def test_quoted_query_operators_are_not_shell_pipelines():
    assert check('oci iam policy list -c "$C" --limit 20 --query \'data[?contains(name, `"test"`) || contains(name, `"demo"`)]\'')['valid']


def test_optional_mcp_uses_real_stdio_without_credentials(tmp_path):
    import asyncio
    import os
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    async def run():
        env = {k: v for k, v in os.environ.items() if not k.startswith('OCI_')}
        env['OCI_CONFIG_FILE'] = str(tmp_path / 'absent')
        parameters = StdioServerParameters(command=sys.executable,
            args=[str(ROOT / 'scripts/command_contract_server.py')], env=env, cwd=tmp_path)
        async with asyncio.timeout(30):
            async with stdio_client(parameters) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = (await session.list_tools()).tools
                    assert {t.name for t in tools} == {'describe_read_command', 'check_read_command'}
                    assert all(t.annotations.readOnlyHint and not t.annotations.openWorldHint for t in tools)
                    result = await session.call_tool('describe_read_command', {'leaf': 'audit event list'})
                    assert not result.isError and json.loads(result.content[0].text)['ok']
                    result = await session.call_tool('check_read_command', {'command': 'oci iam region list --query data'})
                    assert not result.isError and json.loads(result.content[0].text)['valid']
                    result = await session.call_tool('check_read_command', {'command': 'oci budget budget list --limit 10'})
                    assert result.isError and not json.loads(result.content[0].text)['valid']
    asyncio.run(run())
