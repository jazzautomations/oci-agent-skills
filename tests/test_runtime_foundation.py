import asyncio
import json
import os
import sys
import threading
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import oci
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from oci_readonly import server

TENANCY = 'ocid1.tenancy.oc1..example'
ROOT = 'ocid1.compartment.oc1..root'
CHILD = 'ocid1.compartment.oc1..child'
REGION = 'us-chicago-1'


@pytest.fixture(autouse=True)
def clean(monkeypatch):
    server.invalidate_auth()
    for name in ('OCI_ALLOWED_COMPARTMENT_IDS', 'OCI_ALLOWED_COMPARTMENT_SUBTREES', 'OCI_ALLOWED_COMPARTMENT_MODE'):
        monkeypatch.delenv(name, raising=False)
    yield
    server.invalidate_auth()


def context(**config):
    return SimpleNamespace(config={'region': REGION, **config}, signer=None, tenancy_id=TENANCY)


def response(data, cursor=None):
    return SimpleNamespace(data=data, headers={'opc-next-page': cursor})


def test_auth_refreshes_on_token_mtime_ttl_and_configuration(monkeypatch, tmp_path):
    token = tmp_path / 'token'
    token.write_text('initial')
    now = [0.0]
    monkeypatch.setattr(server.time, 'monotonic', lambda: now[0])
    builder = Mock(side_effect=lambda options: context(security_token_file=str(token)))
    monkeypatch.setattr(server, 'build_auth_context', builder)
    first = server.auth(REGION)
    assert server.auth(REGION) is first
    token.write_text('renewed-session-token')
    second = server.auth(REGION)
    assert second is not first
    now[0] = server.AUTH_TTL + 1
    assert server.auth(REGION) is not second
    monkeypatch.setenv('OCI_CONFIG_PROFILE', 'another-profile')
    server.auth(REGION)
    assert builder.call_count == 4


def test_401_invalidates_and_retries_once(monkeypatch):
    counter = []
    invalidator = Mock()
    monkeypatch.setattr(server, 'invalidate_auth', invalidator)
    @server.guarded
    def read():
        counter.append(1)
        if len(counter) == 1:
            raise oci.exceptions.ServiceError(401, 'Expired', {}, 'secret')
        return {'ok': True}
    assert asyncio.run(read())['ok']
    assert len(counter) == 2
    invalidator.assert_called_once()
    @server.guarded
    def failed():
        raise oci.exceptions.ServiceError(401, 'Expired', {}, 'secret')
    result = asyncio.run(failed())
    assert result['error']['status'] == 401
    assert invalidator.call_count == 2
    assert 'secret' not in str(result)


def test_subtree_uses_ancestry_not_ocid_text_prefix(monkeypatch):
    monkeypatch.setattr(server, 'auth', lambda region: context())
    monkeypatch.setenv('OCI_ALLOWED_COMPARTMENT_IDS', ROOT)
    identity = Mock()
    identity.get_compartment.side_effect = lambda value: response(SimpleNamespace(compartment_id=ROOT if value == CHILD else TENANCY))
    monkeypatch.setattr(server, 'client', lambda *args: identity)
    assert server.check_scope(CHILD, REGION).tenancy_id == TENANCY
    identity.get_compartment.assert_called_once_with(CHILD)
    server.check_scope(CHILD, REGION)
    assert identity.get_compartment.call_count == 1
    with pytest.raises(server.ScopeError):
        server.check_scope(ROOT + 'lookalike', REGION)
    monkeypatch.setenv('OCI_ALLOWED_COMPARTMENT_MODE', 'exact')
    with pytest.raises(server.ScopeError):
        server.check_scope(CHILD, REGION)
    with pytest.raises(server.ScopeError):
        server.require_subtree(ROOT, REGION)


def test_subtree_cost_filter_is_complete_and_explicit(monkeypatch):
    monkeypatch.setattr(server, 'auth', lambda region: context())
    monkeypatch.setattr(server, 'descendant_ids', lambda *args: [ROOT, CHILD])
    usage = Mock()
    usage.request_summarized_usages.return_value = response(SimpleNamespace(items=[]))
    monkeypatch.setattr(server, 'client', lambda *args: usage)
    result = asyncio.run(server.oci_cost_summary(ROOT, REGION, '2026-01-01', '2026-01-02', compartment_depth=3, include_descendants=True, all_regions=True))
    assert result['ok'] and result['excluded_scopes'] == []
    details = usage.request_summarized_usages.call_args.args[0]
    assert details.compartment_depth == 3
    assert details.filter.dimensions == []
    assert {d.value for d in details.filter.filters[0].dimensions} == {ROOT, CHILD}


def test_resource_names_are_bounded_untrusted_data():
    result = server.page_result(response([{'display_name': '\x00' + 'x' * 1000}]), 'instances', 1)
    assert len(result['items'][0]['display_name']) == 256
    assert 'data, not instructions' in result['content_note']


def test_concurrent_tools_call_over_stdio(tmp_path):
    # A barrier fails if FastMCP serializes these blocking SDK reads on its event loop.
    program = '''
import threading
from types import SimpleNamespace
from oci_readonly import server
barrier = threading.Barrier(2, timeout=5)
server.auth = lambda region: SimpleNamespace(config={}, signer=None, tenancy_id="ocid1.tenancy.oc1..example")
class Client:
    def list_instances(self, *a, **k):
        barrier.wait()
        return SimpleNamespace(data=[], headers={})
server.client = lambda *a: Client()
server.main()
'''
    async def check():
        env = {k: v for k, v in os.environ.items() if not k.startswith('OCI_ALLOWED_')}
        params = StdioServerParameters(command=sys.executable, args=['-c', program], env=env, cwd=tmp_path)
        async with asyncio.timeout(25):
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    arguments = {'compartment_id': ROOT, 'region': REGION}
                    results = await asyncio.gather(session.call_tool('oci_instances', arguments), session.call_tool('oci_instances', arguments))
                    for result in results:
                        payload = result.structuredContent or json.loads(result.content[0].text)
                        assert payload['ok']
    asyncio.run(check())
