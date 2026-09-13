"""End-to-end semantic checks over raw OCI-shaped CLI responses.

The transport below stands in for the OCI CLI process.  It deliberately returns
raw ``data`` envelopes and evaluates the caller's JMESPath query, so these tests
exercise the real wrapper and workflow code rather than mocked projections.
"""

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import jmespath
import pytest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "runtime"))
from lib import oci_ro  # noqa: E402


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


posture = load("semantic_posture", "skills/oci-security-posture/scripts/posture.py")
waste = load("semantic_waste", "skills/oci-finops-waste/scripts/waste_scan.py")
from oci_readonly import server  # noqa: E402

COMPARTMENT = "ocid1.compartment.oc1..semantic"
TENANCY = "ocid1.tenancy.oc1..semantic"


class RawCLI:
    """Fake ``oci`` process: route raw payloads, then run the requested query."""

    def __init__(self, routes, failures=()):
        self.routes = routes
        self.failures = set(failures)
        self.calls = []

    def __call__(self, argv, **kwargs):
        # ``oci_ro.run`` calls this seam with the original argv; a real
        # subprocess would receive the separately prepared argv.
        command = tuple(argv[argv.index("--cli-rc-file") + 2 :] if "--cli-rc-file" in argv else argv)
        path = []
        for token in command:
            if token.startswith("--"):
                break
            path.append(token)
        key = " ".join(path)
        self.calls.append(command)
        if key in self.failures:
            return SimpleNamespace(returncode=1, stdout="", stderr='{"status": 403}')
        if key not in self.routes:
            raise AssertionError(f"unregistered fake OCI route: {key}")
        raw = self.routes[key]
        query = command[command.index("--query") + 1] if "--query" in command else None
        payload = jmespath.search(query, raw) if query else raw
        return SimpleNamespace(returncode=0, stdout=json.dumps(payload), stderr="")


def patch_cli(monkeypatch, cli):
    monkeypatch.setattr(oci_ro, "run_process", cli)
    monkeypatch.setenv("PROFILE", "test")
    monkeypatch.setenv("REGION", "us-chicago-1")


def test_policy_finding_comes_from_raw_statements_and_query(monkeypatch):
    cli = RawCLI({"iam policy list": {"data": [
        {"name": "broad", "statements": ["Allow any-user to manage all-resources in tenancy"]},
        {"name": "narrow", "statements": ["Allow group Readers to read instances in compartment x"]},
    ]}})
    patch_cli(monkeypatch, cli)
    findings, unread, flags = [], [], []
    posture.policies(COMPARTMENT, findings, unread, flags)
    assert [f["check"] for f in findings] == ["over-broad-policy"]
    assert not unread
    assert any("--query" in call for call in cli.calls)
    assert "broad" not in findings[0]["resource"]


def test_bucket_public_private_classification_survives_hyphenated_query(monkeypatch):
    cli = RawCLI({
        "os ns get": {"data": "namespace"},
        "os bucket list": {"data": [{"name": "private"}, {"name": "public"}]},
        "os bucket get": {"data": {"public-access-type": "ObjectRead", "kms-key-id": None}},
    })
    patch_cli(monkeypatch, cli)
    # Return per bucket detail based on the raw bucket name in each request.
    original = cli
    def routed(argv, **kwargs):
        if "bucket" in argv and "get" in argv:
            name = argv[argv.index("--bucket-name") + 1]
            original.routes["os bucket get"]["data"] = {
                "public-access-type": "NoPublicAccess" if name == "private" else "ObjectRead",
                "kms-key-id": "key" if name == "private" else None,
            }
        return original(argv, **kwargs)
    monkeypatch.setattr(oci_ro, "run_process", routed)
    findings, unread, flags = [], [], []
    posture.buckets(COMPARTMENT, findings, unread, flags)
    assert {f["check"] for f in findings} == {"public-bucket", "bucket-without-cmk"}
    assert len(findings) == 2 and not unread


def test_ingress_ranges_ipv6_and_protocol_are_classified(monkeypatch):
    rules = [
        {"source": "0.0.0.0/0", "protocol": "6", "tcp-options": {"destination-port-range": {"min": 20, "max": 30}}},
        {"source": "::/0", "protocol": "all"},
        {"source": "0.0.0.0/0", "protocol": "17", "udp-options": {"destination-port-range": {"min": 22, "max": 22}}},
        {"source": "10.0.0.0/8", "protocol": "6", "tcp-options": {"destination-port-range": {"min": 22, "max": 22}}},
    ]
    cli = RawCLI({"network security-list list": {"data": [{"display-name": "edge", "ingress-security-rules": rules}]}})
    patch_cli(monkeypatch, cli)
    findings, unread, flags = [], [], []
    posture.ingress(COMPARTMENT, findings, unread, flags)
    assert [f["severity"] for f in findings] == ["CRITICAL", "CRITICAL", "HIGH"]
    assert findings[-1]["severity"] != "CRITICAL"
    assert not unread


def test_failed_policy_read_is_unreadable_not_compliant(monkeypatch):
    cli = RawCLI({}, failures={"iam policy list"})
    patch_cli(monkeypatch, cli)
    findings, unread, flags = [], [], []
    posture.policies(COMPARTMENT, findings, unread, flags)
    assert findings == [] and unread == ["iam policy list"]


def test_posture_preserves_pagination_gap_when_filtered_result_is_small(monkeypatch):
    cli = RawCLI({"iam policy list": {"data": [{"name": "visible", "statements": []}]}})
    patch_cli(monkeypatch, cli)
    original = cli

    def warning_transport(argv, **kwargs):
        response = original(argv, **kwargs)
        response.stderr = "WARNING: not all resources were returned"
        return response

    monkeypatch.setattr(oci_ro, "run_process", warning_transport)
    flags = []
    result = posture.read(["iam", "policy", "list", "--compartment-id", COMPARTMENT,
                           "--limit", "100", "--query", "data[].{n:name,s:statements}"], flags)
    assert result is None
    assert flags


def test_wrapper_executes_jmespath_against_raw_payload(monkeypatch):
    cli = RawCLI({"os bucket get": {"data": {"public-access-type": "ObjectRead", "kms-key-id": "k"}}})
    patch_cli(monkeypatch, cli)
    result = oci_ro.run(["os", "bucket", "get", "--query", 'data.{p:"public-access-type",k:"kms-key-id"}'])
    assert result["ok"] and result["data"]["items"] == {"p": "ObjectRead", "k": "k"}


def test_waste_saturated_attachment_page_cannot_prove_orphan(monkeypatch):
    cli = RawCLI({"compute volume-attachment list": {"data": [{"volume-id": "v1"}, {"volume-id": "v2"}]}})
    patch_cli(monkeypatch, cli)
    scan = waste.Scan("test", "us-chicago-1", TENANCY, [COMPARTMENT], None, limit=2,
                      reader=lambda argv, **kw: oci_ro.run(argv, **kw))
    assert scan.listing("compute volume-attachment list", COMPARTMENT) is None
    assert any(flag.startswith("bounded sample") for flag in scan.flags)


def test_multiattach_requires_all_instances_stopped_before_d3(monkeypatch):
    cli = RawCLI({
        "search resource structured-search": {"data": []},
        "compute instance list": {"data": [{"id": "run", "lifecycle-state": "RUNNING"}, {"id": "stop", "lifecycle-state": "STOPPED"}]},
        "bv volume list": {"data": [{"id": "v", "lifecycle-state": "AVAILABLE", "size-in-gbs": 10, "vpus-per-gb": 10}]},
        "bv boot-volume list": {"data": []},
        "compute volume-attachment list": {"data": [{"volume-id": "v", "instance-id": "run", "lifecycle-state": "ATTACHED"}, {"volume-id": "v", "instance-id": "stop", "lifecycle-state": "ATTACHED"}]},
        "iam availability-domain list": {"data": []},
        "lb load-balancer list": {"data": []}, "nlb network-load-balancer list": {"data": []},
        "bv backup list": {"data": []}, "bv boot-volume-backup list": {"data": []},
        "network public-ip list": {"data": []}, "compute capacity-reservation list": {"data": []},
        "network vcn list": {"data": []}, "network nat-gateway list": {"data": []},
        "ce cluster list": {"data": []}, "os ns get": {"data": "namespace"},
        "os bucket list": {"data": []}, "database db-system list": {"data": []},
    })
    patch_cli(monkeypatch, cli)
    scan = waste.Scan("test", "us-chicago-1", TENANCY, [COMPARTMENT], None,
                      reader=lambda argv, **kw: oci_ro.run(argv, **kw))
    scan.load_balancers = scan.databases = scan.buckets = lambda c: None
    scan.assess_compartment(COMPARTMENT)
    assert "D3" not in {f["pattern"] for f in scan.findings}


def test_failed_attachment_read_does_not_emit_unattached_volume(monkeypatch):
    cli = RawCLI({
        "search resource structured-search": {"data": []},
        "compute instance list": {"data": []},
        "bv volume list": {"data": [{"id": "v", "lifecycle-state": "AVAILABLE", "size-in-gbs": 10, "vpus-per-gb": 10}]},
        "bv boot-volume list": {"data": []}, "compute volume-attachment list": {"error": "failure"},
        "iam availability-domain list": {"data": []}, "lb load-balancer list": {"data": []}, "nlb network-load-balancer list": {"data": []},
        "bv backup list": {"data": []}, "bv boot-volume-backup list": {"data": []}, "network public-ip list": {"data": []},
        "compute capacity-reservation list": {"data": []}, "network vcn list": {"data": []}, "network nat-gateway list": {"data": []},
        "ce cluster list": {"data": []}, "os ns get": {"data": "namespace"}, "os bucket list": {"data": []}, "database db-system list": {"data": []},
    }, failures={"compute volume-attachment list"})
    patch_cli(monkeypatch, cli)
    scan = waste.Scan("test", "us-chicago-1", TENANCY, [COMPARTMENT], None,
                      reader=lambda argv, **kw: oci_ro.run(argv, **kw))
    scan.load_balancers = scan.databases = scan.buckets = lambda c: None
    scan.assess_compartment(COMPARTMENT)
    assert "D1" not in {f["pattern"] for f in scan.findings}
    assert any("volume-attachment" in flag for flag in scan.flags)


def test_detached_attachment_is_ignored_but_complete_empty_list_finds_d1(monkeypatch):
    cli = RawCLI({
        "search resource structured-search": {"data": []}, "compute instance list": {"data": []},
        "bv volume list": {"data": [{"id": "v", "lifecycle-state": "AVAILABLE", "size-in-gbs": 10, "vpus-per-gb": 10}]},
        "bv boot-volume list": {"data": []}, "compute volume-attachment list": {"data": [{"volume-id": "v", "lifecycle-state": "DETACHED"}]},
        "iam availability-domain list": {"data": []}, "lb load-balancer list": {"data": []}, "nlb network-load-balancer list": {"data": []},
        "bv backup list": {"data": []}, "bv boot-volume-backup list": {"data": []}, "network public-ip list": {"data": []},
        "compute capacity-reservation list": {"data": []}, "network vcn list": {"data": []}, "network nat-gateway list": {"data": []},
        "ce cluster list": {"data": []}, "os ns get": {"data": "namespace"}, "os bucket list": {"data": []}, "database db-system list": {"data": []},
    })
    patch_cli(monkeypatch, cli)
    scan = waste.Scan("test", "us-chicago-1", TENANCY, [COMPARTMENT], None,
                      reader=lambda argv, **kw: oci_ro.run(argv, **kw))
    scan.load_balancers = scan.databases = scan.buckets = lambda c: None
    scan.assess_compartment(COMPARTMENT)
    assert "D1" in {f["pattern"] for f in scan.findings}


def test_page_result_marks_oversized_raw_response_incomplete():
    response = SimpleNamespace(data=[{"id": "a", "display_name": "a"}, {"id": "b", "display_name": "b"}], headers={})
    result = server.page_result(response, "instances", 1)
    assert result["items"] == [{"id": "a", "display_name": "a"}]
    assert result["truncated"] and not result["complete"] and result["next_cursor"] is None
    assert result["pagination_error"]


def test_audit_nested_raw_event_is_projected_and_window_is_forwarded(monkeypatch):
    start, end = "2026-01-01T00:00:00Z", "2026-01-01T01:00:00Z"
    event = {"event_time": start, "data": {"event_name": "Launch", "resource_id": "r", "identity": {"principal_id": "p"}, "response": {"status": 200}, "secret": "omit"}}
    class Audit:
        def list_events(self, compartment, got_start, got_end, **kwargs):
            assert (compartment, got_start.isoformat(), got_end.isoformat()) == (COMPARTMENT, "2026-01-01T00:00:00+00:00", "2026-01-01T01:00:00+00:00")
            return SimpleNamespace(data=[event], headers={})
    monkeypatch.setattr(server, "check_scope", lambda *a, **k: None)
    monkeypatch.setattr(server, "client", lambda *a, **k: SimpleNamespace(list_events=Audit().list_events))
    result = server.oci_audit_events.__wrapped__(COMPARTMENT, "us-chicago-1", start, end)
    assert result["items"] == [{"event_time": start, "event_name": "Launch", "principal_id": "p", "resource_id": "r", "status": 200}]
    assert "secret" not in json.dumps(result)


@pytest.mark.parametrize("start,end", [("2026-01-01T01:00:00Z", "2026-01-01T00:00:00Z"), ("2026-01-01T00:00:00", "2026-01-01T01:00:00Z")])
def test_audit_rejects_reverse_or_timezone_less_window(start, end):
    with pytest.raises(ValueError):
        server.bounded_window(start, end)
