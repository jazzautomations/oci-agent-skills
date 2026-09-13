"""Offline execution checks for authored OCI CLI JMESPath projections.

The source query strings are discovered from the repository's command fences;
fixture responses and expected values are intentionally specified separately.
"""

from __future__ import annotations

import json
import shlex
import sys
from pathlib import Path

import jmespath
import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "ci"))
from lint_fences import commands  # noqa: E402
from guard_lib import catalog_data, parse_oci  # noqa: E402


CONTRACTS = json.loads((ROOT / "evals" / "query-response-contracts.json").read_text())["contracts"]


def _commands(path: Path, prefix: str) -> list[str]:
    return [command for _line, command in commands(path.read_text())
            if command.startswith(prefix + " ") or command == prefix]


def _extract_query(path: str, prefix: str, occurrence: int = 0) -> str:
    matches = _commands(ROOT / path, prefix)
    assert len(matches) > occurrence, f"source command disappeared: {path}: {prefix}"
    argv = shlex.split(matches[occurrence], comments=True)
    index = argv.index("--query")
    return argv[index + 1]


def _extract_command(path: str, prefix: str, occurrence: int = 0):
    return shlex.split(_commands(ROOT / path, prefix)[occurrence], comments=True)


def _binding(query):
    binding = SOURCE_BINDINGS[query]
    return (*binding, 0) if len(binding) == 3 else binding


def _case(query: str, response: dict, expected):
    return query, response, expected


# Each response is an OCI CLI-shaped document. Expected values are authored by
# hand and do not come from evaluating the query.
CASES = [
    _case('data[].name', {"data": [{"name": "iad"}, {"name": "phx"}]}, ["iad", "phx"]),
    _case('data[].{id:id,state:"lifecycle-state",shape:shape}', {"data": [{"id": "i-1", "lifecycle-state": "RUNNING", "shape": "VM.Standard.E5"}]}, [{"id": "i-1", "state": "RUNNING", "shape": "VM.Standard.E5"}]),
    _case('data.items[].{id:id,name:"display-name",state:"lifecycle-state"}', {"data": {"items": [{"id": "p-1", "display-name": "dev", "lifecycle-state": "ACTIVE"}]}}, [{"id": "p-1", "name": "dev", "state": "ACTIVE"}]),
    _case('data.items[].{id:id,name:name,state:"lifecycle-state"}', {"data": {"items": [{"id": "r-1", "name": "resource", "lifecycle-state": "FAILED"}]}}, [{"id": "r-1", "name": "resource", "state": "FAILED"}]),
    _case('data[].{id:id,operation:operation,state:"lifecycle-state"}', {"data": [{"id": "job-1", "operation": "PLAN", "lifecycle-state": "SUCCEEDED"}]}, [{"id": "job-1", "operation": "PLAN", "state": "SUCCEEDED"}]),
    _case('data.{state:"lifecycle-state",mtls:"is-mtls-connection-required",acl:"whitelisted-ips"}', {"data": {"lifecycle-state": "AVAILABLE", "is-mtls-connection-required": False, "whitelisted-ips": ["10.0.0.0/8"]}}, {"state": "AVAILABLE", "mtls": False, "acl": ["10.0.0.0/8"]}),
    _case('data[].{id:id,state:"lifecycle-state",type:type}', {"data": [{"id": "b-1", "lifecycle-state": "SUCCEEDED", "type": "FULL"}, {"id": "b-2", "lifecycle-state": "FAILED", "type": "INCREMENTAL"}]}, [{"id": "b-1", "state": "SUCCEEDED", "type": "FULL"}, {"id": "b-2", "state": "FAILED", "type": "INCREMENTAL"}]),
    _case('data[?status!=`SUCCEEDED`].{op:"operation-type",s:status}', {"data": [{"operation-type": "CREATE", "status": "SUCCEEDED"}, {"operation-type": "DELETE", "status": "FAILED"}]}, [{"op": "DELETE", "s": "FAILED"}]),
    _case('data[?status!=`OK`].{a:"display-name",s:status}', {"data": [{"display-name": "healthy", "status": "OK"}, {"display-name": "api", "status": "CRITICAL"}]}, [{"a": "api", "s": "CRITICAL"}]),
    _case('data[?"is-mfa-activated"==`false`].{n:name,st:"lifecycle-state"}', {"data": [{"name": "alice", "is-mfa-activated": False, "lifecycle-state": "ACTIVE"}, {"name": "bob", "is-mfa-activated": None, "lifecycle-state": "ACTIVE"}, {"name": "carol", "is-mfa-activated": True, "lifecycle-state": "ACTIVE"}]}, [{"n": "alice", "st": "ACTIVE"}]),
    _case('data[?"is-free-tier"].{n:"display-name",st:"lifecycle-state",cpu:"cpu-core-count"}', {"data": [{"display-name": "free", "is-free-tier": True, "lifecycle-state": "AVAILABLE", "cpu-core-count": 1}, {"display-name": "paid", "is-free-tier": False, "lifecycle-state": "AVAILABLE", "cpu-core-count": 2}]}, [{"n": "free", "st": "AVAILABLE", "cpu": 1}]),
    _case('data[?contains(shape,`A1`)||contains(shape,`Micro`)].shape', {"data": [{"shape": "VM.Standard.A1.Flex"}, {"shape": "VM.Standard.E4.Flex"}, {"shape": "VM.Standard.E2.1.Micro"}]}, ["VM.Standard.A1.Flex", "VM.Standard.E2.1.Micro"]),
    _case('data[].{name:"display-name",routes:"route-rules"[?contains(`["0.0.0.0/0","::/0"]`,destination)]} | [?length(routes) > `0`]', {"data": [{"display-name": "public", "route-rules": [{"destination": "0.0.0.0/0", "network-entity-id": "igw"}]}, {"display-name": "private", "route-rules": [{"destination": "10.0.0.0/16"}]}]}, [{"name": "public", "routes": [{"destination": "0.0.0.0/0", "network-entity-id": "igw"}]}]),
    _case('data[].{n:name,broad:statements[?contains(@,`"any-user"`) || contains(@,`"manage all-resources"`)]} | [?length(broad) > `0`]', {"data": [{"name": "wide", "statements": ["Allow any-user to manage all-resources in tenancy"]}, {"name": "narrow", "statements": ["Allow group ops to read buckets"]}]}, [{"n": "wide", "broad": ["Allow any-user to manage all-resources in tenancy"]}]),
    _case('data[].{t:"event-time",who:data.identity."principal-name",what:"event-type",status:data.response.status}', {"data": [{"event-time": "2026-01-01T00:00:00Z", "data": {"identity": {"principal-name": "alice"}, "response": {"status": "200"}}, "event-type": "CreateBucket"}]}, [{"t": "2026-01-01T00:00:00Z", "who": "alice", "what": "CreateBucket", "status": "200"}]),
    _case('data[].{n:"display-name",open:"ingress-security-rules"[?source==`0.0.0.0/0` || source==`::/0`]}', {'data': [{'display-name': 'public', 'ingress-security-rules': [{'source': '0.0.0.0/0', 'protocol': '6', 'tcp-options': {'destination-port-range': {'min': 20, 'max': 30}}, 'is-stateless': False}, {'source': '::/0', 'protocol': 'all', 'is-stateless': True}, {'source': '0.0.0.0/0', 'protocol': '17', 'udp-options': {'destination-port-range': {'min': 22, 'max': 22}}, 'is-stateless': False}, {'source': '10.0.0.0/8', 'protocol': '6'}]}, {'display-name': 'private', 'ingress-security-rules': []}]}, [{'n': 'public', 'open': [{'source': '0.0.0.0/0', 'protocol': '6', 'tcp-options': {'destination-port-range': {'min': 20, 'max': 30}}, 'is-stateless': False}, {'source': '::/0', 'protocol': 'all', 'is-stateless': True}, {'source': '0.0.0.0/0', 'protocol': '17', 'udp-options': {'destination-port-range': {'min': 22, 'max': 22}}, 'is-stateless': False}]}, {'n': 'private', 'open': []}]),
    _case('data.items[].{r:"resource-name",rule:"detector-rule-id"}', {"data": {"items": [{"resource-name": "bucket-a", "detector-rule-id": "rule-1"}]}}, [{"r": "bucket-a", "rule": "rule-1"}]),
    _case('data.{id:id,state:"lifecycle-state",progress:"build-run-progress"}', {"data": {"id": "run-fail", "lifecycle-state": "FAILED", "build-run-progress": 42}}, {"id": "run-fail", "state": "FAILED", "progress": 42}),
    _case('data[].{op:"operation-type",status:status,pct:"percent-complete",id:id}', {"data": [{"operation-type": "CREATE", "status": "IN_PROGRESS", "percent-complete": 60, "id": "op-1"}]}, [{"op": "CREATE", "status": "IN_PROGRESS", "pct": 60, "id": "op-1"}]),
    _case('data.items[].{id:id,state:"lifecycle-state",type:type}', {"data": {"items": [{"id": "db-1", "lifecycle-state": "AVAILABLE", "type": "PRIMARY"}]}}, [{"id": "db-1", "state": "AVAILABLE", "type": "PRIMARY"}]),
    _case('data[].{id:id,mode:"protection-mode",state:"lifecycle-state"}', {"data": [{"id": "key-1", "protection-mode": "HSM", "lifecycle-state": "ENABLED"}]}, [{"id": "key-1", "mode": "HSM", "state": "ENABLED"}]),
    _case('data.items[].{id:id,expires:"current-version-summary".validity."time-of-validity-not-after"}', {"data": {"items": [{"id": "cert-1", "current-version-summary": {"validity": {"time-of-validity-not-after": "2027-01-01T00:00:00Z"}}}]}}, [{"id": "cert-1", "expires": "2027-01-01T00:00:00Z"}]),
    _case('data[].{state:"lifecycle-state",created:"time-created"}', {"data": [{"lifecycle-state": "AVAILABLE", "time-created": "2026-02-01T00:00:00Z"}]}, [{"state": "AVAILABLE", "created": "2026-02-01T00:00:00Z"}]),
    _case('data[].{id:id,source:"volume-id",state:"lifecycle-state"}', {"data": [{"id": "bak-1", "volume-id": "vol-1", "lifecycle-state": "AVAILABLE"}]}, [{"id": "bak-1", "source": "vol-1", "state": "AVAILABLE"}]),
    _case('data.items[].{id:id,shape:shape,state:"lifecycle-state"}', {"data": {"items": [{"id": "ci-1", "shape": "CI.Standard.E4.Flex", "lifecycle-state": "RUNNING"}]}}, [{"id": "ci-1", "shape": "CI.Standard.E4.Flex", "state": "RUNNING"}]),
    _case('data.items[].{id:id,type:"endpoint-type",state:"lifecycle-state"}', {"data": {"items": [{"id": "gw-1", "endpoint-type": "PUBLIC", "lifecycle-state": "ACTIVE"}]}}, [{"id": "gw-1", "type": "PUBLIC", "state": "ACTIVE"}]),
    _case('data[].{n:name,v:value,ad:"availability-domain"}', {"data": [{"name": "vm-standard", "value": 3, "availability-domain": "AD-1"}, {"name": "vm-standard", "value": 1, "availability-domain": "AD-2"}]}, [{"n": "vm-standard", "v": 3, "ad": "AD-1"}, {"n": "vm-standard", "v": 1, "ad": "AD-2"}]),
    _case('data.{used:used,available:available,quota:"effective-quota-value"}', {"data": {"used": 2, "available": 8, "effective-quota-value": 10}}, {"used": 2, "available": 8, "quota": 10}),
    _case('data.items[].{service:service,amount:"computed-amount",currency:currency,start:"time-usage-started",end:"time-usage-ended"}', {"data": {"items": [{"service": "Compute", "computed-amount": 12.5, "currency": "USD", "time-usage-started": "2026-01-01", "time-usage-ended": "2026-02-01"}, {"service": "Storage", "computed-amount": 900, "currency": "JPY", "time-usage-started": "2026-01-01", "time-usage-ended": "2026-02-01"}]}}, [{"service": "Compute", "amount": 12.5, "currency": "USD", "start": "2026-01-01", "end": "2026-02-01"}, {"service": "Storage", "amount": 900, "currency": "JPY", "start": "2026-01-01", "end": "2026-02-01"}]),
    _case('data.items[].{service:service,sku:"sku-name",amount:"computed-amount",currency:currency,start:"time-usage-started",end:"time-usage-ended"}', {"data": {"items": [{"service": "Compute", "sku-name": "OCPU", "computed-amount": 4.2, "currency": "USD", "time-usage-started": "2026-01-01", "time-usage-ended": "2026-01-02"}, {"service": "Storage", "sku-name": "GB", "computed-amount": 700, "currency": "JPY", "time-usage-started": "2026-01-02", "time-usage-ended": "2026-01-03"}]}}, [{"service": "Compute", "sku": "OCPU", "amount": 4.2, "currency": "USD", "start": "2026-01-01", "end": "2026-01-02"}, {"service": "Storage", "sku": "GB", "amount": 700, "currency": "JPY", "start": "2026-01-02", "end": "2026-01-03"}]),
    _case('data[].{id:id,architecture:shape,subnets:"subnet-ids"}', {"data": [{"id": "app-1", "shape": "GENERIC_X86", "subnet-ids": ["sub-1", "sub-2"]}]}, [{"id": "app-1", "architecture": "GENERIC_X86", "subnets": ["sub-1", "sub-2"]}]),
    _case('data[].{protocol:protocol,state:"lifecycle-state"}', {"data": [{"protocol": "EMAIL", "lifecycle-state": "ACTIVE"}]}, [{"protocol": "EMAIL", "state": "ACTIVE"}]),
    _case('data[].{id:id,state:state}', {"data": []}, []),
]


# Explicit provenance keeps a matching query in an unrelated example/model
# from silently satisfying a scenario. Contract names are present where the
# repository has a response schema for that CLI leaf.
SOURCE_BINDINGS = {
    'data[].name': ('skills/oci-compute/SKILL.md', 'oci iam availability-domain list', None),
    'data[].{id:id,state:"lifecycle-state",shape:shape}': ('skills/oci-compute/SKILL.md', 'oci compute instance list', 'compute instance list'),
    'data.items[].{id:id,name:"display-name",state:"lifecycle-state"}': ('skills/oci-support-limits/references/limit-increase.md', 'oci limits-increase limits-increase-request list', None),
    'data.items[].{id:id,name:name,state:"lifecycle-state"}': ('skills/oci-devops-pipelines/SKILL.md', 'oci devops project list', None),
    'data[].{id:id,operation:operation,state:"lifecycle-state"}': ('skills/oci-terraform/SKILL.md', 'oci resource-manager job list', None),
    'data.{state:"lifecycle-state",mtls:"is-mtls-connection-required",acl:"whitelisted-ips"}': ('skills/oracle-autonomous-db/SKILL.md', 'oci db autonomous-database get', None),
    'data[].{id:id,state:"lifecycle-state",type:type}': ('skills/oracle-autonomous-db/SKILL.md', 'oci db autonomous-database-backup list', None),
    'data[?status!=`SUCCEEDED`].{op:"operation-type",s:status}': ('skills/oci-incident-triage/SKILL.md', 'oci work-requests work-request list', 'work-requests work-request list'),
    'data[?status!=`OK`].{a:"display-name",s:status}': ('skills/oci-incident-triage/SKILL.md', 'oci monitoring alarm-status list-alarms-status', None),
    'data[?"is-mfa-activated"==`false`].{n:name,st:"lifecycle-state"}': ('skills/oci-security-posture/SKILL.md', 'oci iam user list', None),
    'data[?"is-free-tier"].{n:"display-name",st:"lifecycle-state",cpu:"cpu-core-count"}': ('skills/oci-free-tier/references/lifecycle-clocks.md', 'oci db autonomous-database list', None),
    'data[?contains(shape,`A1`)||contains(shape,`Micro`)].shape': ('skills/oci-free-tier/SKILL.md', 'oci compute shape list', 'compute shape list'),
    'data[].{name:"display-name",routes:"route-rules"[?contains(`["0.0.0.0/0","::/0"]`,destination)]} | [?length(routes) > `0`]': ('skills/oci-networking/SKILL.md', 'oci network route-table list', 'network route-table list'),
    'data[].{n:name,broad:statements[?contains(@,`"any-user"`) || contains(@,`"manage all-resources"`)]} | [?length(broad) > `0`]' : ('skills/oci-security-posture/SKILL.md', 'oci iam policy list', 'iam policy list'),
    'data[].{t:"event-time",who:data.identity."principal-name",what:"event-type",status:data.response.status}': ('skills/oci-logging-audit/SKILL.md', 'oci audit event list', 'audit event list'),
    'data[].{n:"display-name",open:"ingress-security-rules"[?source==`0.0.0.0/0` || source==`::/0`]}': ('skills/oci-security-posture/SKILL.md', 'oci network security-list list', 'network security-list list'),
    'data.items[].{r:"resource-name",rule:"detector-rule-id"}': ('skills/oci-security-posture/SKILL.md', 'oci cloud-guard problem list', 'cloud-guard problem list'),
    'data.{id:id,state:"lifecycle-state",progress:"build-run-progress"}': ('skills/oci-devops-pipelines/SKILL.md', 'oci devops build-run get', None),
    'data[].{op:"operation-type",status:status,pct:"percent-complete",id:id}': ('skills/oci-cli-auth/SKILL.md', 'oci work-requests work-request list', 'work-requests work-request list'),
    'data.items[].{id:id,state:"lifecycle-state",type:type}': ('skills/oracle-db-sql-access/SKILL.md', 'oci dbtools connection list', None),
    'data[].{id:id,mode:"protection-mode",state:"lifecycle-state"}': ('skills/oci-vault-certificates/SKILL.md', 'oci kms management key list', None),
    'data.items[].{id:id,expires:"current-version-summary".validity."time-of-validity-not-after"}': ('skills/oci-vault-certificates/SKILL.md', 'oci certs-mgmt certificate list', None),
    'data[].{state:"lifecycle-state",created:"time-created"}': ('skills/oci-dr-backup/SKILL.md', 'oci bv backup list', None),
    'data[].{id:id,source:"volume-id",state:"lifecycle-state"}': ('skills/oci-block-file-storage/SKILL.md', 'oci bv backup list', None),
    'data.items[].{id:id,shape:shape,state:"lifecycle-state"}': ('skills/oci-serverless/SKILL.md', 'oci container-instances container-instance list', None),
    'data.items[].{id:id,type:"endpoint-type",state:"lifecycle-state"}': ('skills/oci-serverless/SKILL.md', 'oci api-gateway gateway list', None),
    'data[].{n:name,v:value,ad:"availability-domain"}': ('skills/oci-support-limits/SKILL.md', 'oci limits value list', None),
    'data.{used:used,available:available,quota:"effective-quota-value"}': ('skills/oci-free-tier/SKILL.md', 'oci limits resource-availability get', None),
    'data.items[].{service:service,amount:"computed-amount",currency:currency,start:"time-usage-started",end:"time-usage-ended"}': ('skills/oci-cost-analysis/SKILL.md', 'oci usage-api usage-summary request-summarized-usages', 'usage-api usage-summary request-summarized-usages', 0),
    'data.items[].{service:service,sku:"sku-name",amount:"computed-amount",currency:currency,start:"time-usage-started",end:"time-usage-ended"}': ('skills/oci-cost-analysis/SKILL.md', 'oci usage-api usage-summary request-summarized-usages', 'usage-api usage-summary request-summarized-usages', 1),
    'data[].{id:id,architecture:shape,subnets:"subnet-ids"}': ('skills/oci-serverless/SKILL.md', 'oci fn application list', None),
    'data[].{protocol:protocol,state:"lifecycle-state"}': ('skills/oci-monitoring-alarms/SKILL.md', 'oci ons subscription list', None),
    'data[].{id:id,state:state}': ('skills/oci-compute/SKILL.md', 'oci compute-management instance-pool list-instances', None),
}




CASES.extend([('data[].{id:id,direction:direction,source:source,sourceType:"source-type",destination:destination,destinationType:"destination-type",protocol:protocol,tcp:"tcp-options",udp:"udp-options",icmp:"icmp-options",stateless:"is-stateless"}', {'data': [{'id': 'ingress', 'direction': 'INGRESS', 'source': '::/0', 'source-type': 'CIDR_BLOCK', 'protocol': '6', 'tcp-options': {'destination-port-range': {'min': 20, 'max': 30}}, 'is-stateless': False}, {'id': 'egress', 'direction': 'EGRESS', 'destination': '0.0.0.0/0', 'destination-type': 'CIDR_BLOCK', 'protocol': '17', 'udp-options': {'destination-port-range': {'min': 53, 'max': 53}}, 'is-stateless': True}]}, [{'id': 'ingress', 'direction': 'INGRESS', 'source': '::/0', 'sourceType': 'CIDR_BLOCK', 'destination': None, 'destinationType': None, 'protocol': '6', 'tcp': {'destination-port-range': {'min': 20, 'max': 30}}, 'udp': None, 'icmp': None, 'stateless': False}, {'id': 'egress', 'direction': 'EGRESS', 'source': None, 'sourceType': None, 'destination': '0.0.0.0/0', 'destinationType': 'CIDR_BLOCK', 'protocol': '17', 'tcp': None, 'udp': {'destination-port-range': {'min': 53, 'max': 53}}, 'icmp': None, 'stateless': True}]), ('data[].{id:id,name:name,version:"kubernetes-version",size:"node-config-details".size}', {'data': [{'id': 'p1', 'name': 'workers', 'kubernetes-version': 'v1.34.0', 'node-config-details': {'size': 3}}, {'id': 'p2', 'name': 'legacy', 'kubernetes-version': 'v1.33.0', 'node-config-details': {}}]}, [{'id': 'p1', 'name': 'workers', 'version': 'v1.34.0', 'size': 3}, {'id': 'p2', 'name': 'legacy', 'version': 'v1.33.0', 'size': None}]), ('data.items[].{tags:tags,amount:"computed-amount",currency:currency,start:"time-usage-started",end:"time-usage-ended"}', {'data': {'items': [{'tags': [{'namespace': 'Team', 'key': 'owner', 'value': 'ops'}, {'namespace': 'CostCenter', 'key': 'project', 'value': 'demo'}], 'computed-amount': 1.25, 'currency': 'USD', 'time-usage-started': '2026-01-01', 'time-usage-ended': '2026-02-01'}]}}, [{'tags': [{'namespace': 'Team', 'key': 'owner', 'value': 'ops'}, {'namespace': 'CostCenter', 'key': 'project', 'value': 'demo'}], 'amount': 1.25, 'currency': 'USD', 'start': '2026-01-01', 'end': '2026-02-01'}])])
SOURCE_BINDINGS.update({'data[].{id:id,direction:direction,source:source,sourceType:"source-type",destination:destination,destinationType:"destination-type",protocol:protocol,tcp:"tcp-options",udp:"udp-options",icmp:"icmp-options",stateless:"is-stateless"}': ('skills/oci-networking/SKILL.md', 'oci network nsg rules list', 'network nsg rules list'), 'data[].{id:id,name:name,version:"kubernetes-version",size:"node-config-details".size}': ('skills/oci-oke/SKILL.md', 'oci ce node-pool list', 'ce node-pool list'), 'data.items[].{tags:tags,amount:"computed-amount",currency:currency,start:"time-usage-started",end:"time-usage-ended"}': ('skills/oci-cost-analysis/SKILL.md', 'oci usage-api usage-summary request-summarized-usages', 'usage-api usage-summary request-summarized-usages', 2)})

@pytest.mark.parametrize("query,response,expected", CASES, ids=[f"Q{i:02d}" for i in range(1, len(CASES) + 1)])
def test_authored_query_has_explicit_read_source(query, response, expected):
    del response, expected
    source_path, prefix, _contract, occurrence = _binding(query)
    extracted = _extract_query(source_path, prefix, occurrence)
    assert extracted == query
    argv = _extract_command(source_path, prefix, occurrence)
    leaves, _ = catalog_data()
    leaf, _options = parse_oci(argv[1:])
    assert leaves[leaf]["read_only"], f"source command is not read-only: {prefix}"


@pytest.mark.parametrize("query,response,expected", CASES, ids=[f"Q{i:02d}" for i in range(1, len(CASES) + 1)])
def test_authored_query_has_expected_offline_semantics(query, response, expected):
    source_path, prefix, contract, occurrence = _binding(query)
    extracted = _extract_query(source_path, prefix, occurrence)
    actual = jmespath.search(extracted, response)
    assert actual == expected, f"unexpected result for {source_path} ({prefix})"
    if contract:
        errors = list(Draft202012Validator(CONTRACTS[contract]["response"]).iter_errors(response))
        assert not errors, f"fixture violates {contract} response contract: {errors[0].message}"


def test_case_data_remains_json_serializable():
    for _query, response, expected in CASES:
        json.dumps({"response": response, "expected": expected})


def test_node_pool_null_configuration_remains_unknown():
    # Null robustness is separate from the conservative SDK field/type schema.
    query = _extract_query("skills/oci-oke/SKILL.md", "oci ce node-pool list")
    response = {"data": [{"id": "legacy", "name": "old", "kubernetes-version": "v1.33.0", "node-config-details": None}]}
    assert jmespath.search(query, response) == [{"id": "legacy", "name": "old", "version": "v1.33.0", "size": None}]
