import asyncio
from types import SimpleNamespace
from unittest.mock import Mock, create_autospec
import oci
import pytest
from oci_readonly import server
from oci_readonly.smoke import EXPECTED, run
TENANCY = 'ocid1.tenancy.oc1..example'
COMPARTMENT = 'ocid1.compartment.oc1..example'
REGION = 'us-chicago-1'

@pytest.fixture
def context(monkeypatch):
    value = SimpleNamespace(config={'region': REGION}, signer=None, tenancy_id=TENANCY)
    monkeypatch.setattr(server, 'auth', lambda region: value)
    monkeypatch.delenv('OCI_ALLOWED_COMPARTMENT_IDS', raising=False)
    return value

def response(rows, cursor=None):
    return SimpleNamespace(data=rows, headers={'opc-next-page': cursor})

def test_tool_surface_is_fixed_and_readonly():
    tools = asyncio.run(server.mcp.list_tools())
    assert {tool.name for tool in tools} == EXPECTED
    for tool in tools:
        assert tool.annotations.readOnlyHint is True
        assert tool.annotations.destructiveHint is False
        assert tool.annotations.idempotentHint is True

@pytest.mark.parametrize('value', ['bad', "ocid1.compartment.oc1..bad'", 'ocid1.compartment.oc1..bad\n', 'ocid1.compartment.oc1..bad && x', 'ocid1.instance.oc1..example'])
def test_scope_rejects_non_identifiers(value):
    with pytest.raises(server.ScopeError):
        server.scope_id(value)

def test_allowlist_is_exact_and_checks_before_client(context, monkeypatch):
    monkeypatch.setenv('OCI_ALLOWED_COMPARTMENT_IDS', COMPARTMENT)
    monkeypatch.setenv('OCI_ALLOWED_COMPARTMENT_MODE', 'exact')
    factory = Mock()
    monkeypatch.setattr(server, 'client', factory)
    assert asyncio.run(server.oci_instances(TENANCY, REGION))['error']['kind'] == 'invalid_scope'
    factory.assert_not_called()
    assert server.check_scope(COMPARTMENT, REGION) is context

def test_tenancy_tools_cannot_choose_other_tenancy(context):
    assert asyncio.run(server.oci_regions('ocid1.tenancy.oc1..other', REGION))['error']['kind'] == 'invalid_scope'

def test_bad_auth_configuration_is_distinct_and_sanitized(monkeypatch):
    server.auth.cache_clear()
    monkeypatch.setattr(server, 'build_auth_context', Mock(side_effect=ValueError('secret-path')))
    result = asyncio.run(server.oci_instances(COMPARTMENT, REGION))
    assert result['error']['kind'] == 'authentication'
    assert 'secret-path' not in str(result)
    server.auth.cache_clear()

def test_page_preserves_cursor_and_excludes_secrets():
    result = server.page_result(response([{'id': 'id', 'display_name': 'vm', 'metadata': {'ssh': 'secret'}, 'freeform_tags': {'token': 'secret'}, 'private_ip': 'secret'}], 'next'), 'instances', 1)
    assert result['items'] == [{'id': 'id', 'display_name': 'vm'}]
    assert result['next_cursor'] == 'next'
    assert result['truncated'] is True

def test_oversized_page_does_not_silently_skip_rows():
    result = server.page_result(response([{'id': str(i)} for i in range(3)], 'next'), 'instances', 2)
    assert result['count'] == 2
    assert result['truncated'] is True
    assert result['next_cursor'] is None
    assert result['pagination_error']

def test_empty_last_page():
    result = server.page_result(response([]), 'instances', 1)
    assert result['count'] == 0
    assert result['truncated'] is False
    assert result['next_cursor'] is None

@pytest.mark.parametrize('size', [0, 101])
def test_page_size_bounds(size):
    with pytest.raises(ValueError):
        server.page_result(response([]), 'instances', size)

@pytest.mark.parametrize('signer', [None, object()])
def test_client_carries_auth_user_agent_and_timeout(context, signer):
    context.signer = signer
    factory = Mock()
    server.client(factory, REGION)
    config = factory.call_args.args[0]
    kwargs = factory.call_args.kwargs
    assert config['additional_user_agent'] == 'oci-readonly-mcp/0.1.0'
    assert 'additional_user_agent' not in context.config
    assert kwargs['timeout'] == (5, 25)
    assert isinstance(kwargs['retry_strategy'], oci.retry.NoneRetryStrategy)
    assert kwargs.get('signer') is signer

@pytest.mark.parametrize('error,kind', [(ValueError('secret'), 'invalid_input'), (RuntimeError('secret'), 'configuration_or_transport'), (oci.exceptions.ServiceError(403, 'secret', {}, 'secret'), 'oci_service')])
def test_errors_never_echo_exception_or_headers(context, monkeypatch, error, kind):
    monkeypatch.setattr(server, 'client', Mock(side_effect=error))
    result = asyncio.run(server.oci_instances(COMPARTMENT, REGION))
    assert result['error']['kind'] == kind
    assert 'secret' not in str(result)

def test_one_page_call_passes_exact_scope_and_cursor(context, monkeypatch):
    compute = Mock()
    compute.list_instances.return_value = response([], 'next')
    monkeypatch.setattr(server, 'client', lambda factory, region: compute)
    result = asyncio.run(server.oci_instances(COMPARTMENT, REGION, 2, 'previous'))
    compute.list_instances.assert_called_once_with(COMPARTMENT, limit=2, page='previous')
    assert result['next_cursor'] == 'next'

def test_search_uses_only_validated_compartment(context, monkeypatch):
    search = Mock()
    search.search_resources.return_value = response(SimpleNamespace(items=[]))
    monkeypatch.setattr(server, 'client', lambda factory, region: search)
    assert asyncio.run(server.oci_resource_search(COMPARTMENT, REGION))['ok']
    query = search.search_resources.call_args.args[0].query
    assert query == f"query all resources where compartmentId = '{COMPARTMENT}'"

@pytest.mark.parametrize('resource', ['vcns', 'subnets', 'network_security_groups'])
def test_network_uses_real_sdk_signature(context, monkeypatch, resource):
    network = create_autospec(oci.core.VirtualNetworkClient, instance=True)
    operation = getattr(network, 'list_' + resource)
    operation.return_value = response([])
    monkeypatch.setattr(server, 'client', lambda factory, region: network)
    assert asyncio.run(server.oci_network_inventory(COMPARTMENT, REGION, resource))['ok']
    operation.assert_called_once_with(compartment_id=COMPARTMENT, limit=50, page=None)

def test_cost_filters_exact_compartment_region_and_rejects_unbounded_window(context, monkeypatch):
    usage = Mock()
    usage.request_summarized_usages.return_value = response(SimpleNamespace(items=[]))
    monkeypatch.setattr(server, 'client', lambda factory, region: usage)
    assert not asyncio.run(server.oci_cost_summary(COMPARTMENT, REGION, '2026-01-01', '2026-03-01'))['ok']
    usage.request_summarized_usages.assert_not_called()
    assert asyncio.run(server.oci_cost_summary(COMPARTMENT, REGION, '2026-01-01', '2026-01-02'))['ok']
    details = usage.request_summarized_usages.call_args.args[0]
    assert details.tenant_id == TENANCY
    assert details.filter.operator == 'AND'
    assert {d.key: d.value for d in details.filter.dimensions} == {'compartmentId': COMPARTMENT, 'region': REGION}

def test_stdio_starts_without_credentials_and_rejects_bad_scope(monkeypatch):
    monkeypatch.setenv('OCI_CONFIG_FILE', '/nonexistent/oci-config')
    report = asyncio.run(run(False, REGION, 20))
    assert report['ok'] is True
    assert report['tool_count'] == 9
