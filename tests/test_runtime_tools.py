import asyncio
from types import SimpleNamespace
from unittest.mock import create_autospec

import oci
import pytest
from oci_readonly import server

COMPARTMENT = "ocid1.compartment.oc1..example"
OTHER = "ocid1.compartment.oc1..other"
TENANCY = "ocid1.tenancy.oc1..example"
REGION = "us-chicago-1"
WINDOW = ("2026-01-01T00:00:00Z", "2026-01-01T01:00:00Z")


def response(data, cursor=None):
    return SimpleNamespace(data=data, headers={"opc-next-page": cursor})


@pytest.fixture(autouse=True)
def context(monkeypatch):
    server.invalidate_auth()
    value = SimpleNamespace(
        config={"region": REGION, "key_content": "secret"},
        signer=None,
        tenancy_id=TENANCY,
        region=REGION,
        profile_name="DEFAULT",
        auth_type="api_key",
    )
    monkeypatch.setattr(server, "auth", lambda region: value)
    monkeypatch.setattr(server, "build_auth_context", lambda options: value)
    for name in ("OCI_ALLOWED_COMPARTMENT_IDS", "OCI_ALLOWED_COMPARTMENT_SUBTREES"):
        monkeypatch.delenv(name, raising=False)
    return value


def test_whoami_never_exposes_auth_config(monkeypatch):
    identity = create_autospec(oci.identity.IdentityClient, instance=True)
    identity.get_tenancy.return_value = response(
        oci.identity.models.Tenancy(name="Example", id=TENANCY)
    )
    identity.list_region_subscriptions.return_value = response([])
    monkeypatch.setattr(server, "client", lambda *args: identity)
    result = asyncio.run(server.oci_whoami())
    assert result["ok"] and result["count"] == 1
    assert result["items"][0]["tenancy_id"] == TENANCY
    assert "secret" not in str(result) and "key_content" not in str(result)


@pytest.mark.parametrize(
    "detail,operation",
    [
        ("summary", None),
        ("errors", "list_work_request_errors"),
        ("logs", "list_work_request_logs"),
    ],
)
def test_work_request_scope_and_projection(monkeypatch, detail, operation):
    work = create_autospec(oci.work_requests.WorkRequestClient, instance=True)
    work.get_work_request.return_value = response(
        oci.work_requests.models.WorkRequest(
            id="id", compartment_id=COMPARTMENT, status="SUCCEEDED"
        )
    )
    if operation:
        getattr(work, operation).return_value = response(
            [{"message": "Bearer secret", "timestamp": "now", "private": "secret"}],
            "next",
        )
    monkeypatch.setattr(server, "client", lambda *args: work)
    result = asyncio.run(
        server.oci_work_requests(
            COMPARTMENT, REGION, "ocid1.workrequest.oc1..example", detail=detail
        )
    )
    assert result["ok"]
    assert "secret" not in str(result)
    work.get_work_request.return_value.data.compartment_id = OTHER
    assert (
        asyncio.run(
            server.oci_work_requests(
                COMPARTMENT, REGION, "ocid1.workrequest.oc1..example", detail=detail
            )
        )["error"]["kind"]
        == "invalid_scope"
    )


def test_alarm_status_and_history(monkeypatch):
    monitoring = create_autospec(oci.monitoring.MonitoringClient, instance=True)
    monitoring.list_alarms_status.return_value = response([])
    monitoring.get_alarm.return_value = response(
        oci.monitoring.models.Alarm(compartment_id=COMPARTMENT)
    )
    monitoring.get_alarm_history.return_value = response(
        oci.monitoring.models.AlarmHistoryCollection(entries=[])
    )
    monkeypatch.setattr(server, "client", lambda *args: monitoring)
    assert asyncio.run(server.oci_alarm_status(COMPARTMENT, REGION))["ok"]
    assert asyncio.run(
        server.oci_alarm_status(
            COMPARTMENT, REGION, "ocid1.alarm.oc1..example", *WINDOW
        )
    )["ok"]
    assert not asyncio.run(
        server.oci_alarm_status(
            COMPARTMENT,
            REGION,
            "ocid1.alarm.oc1..example",
            WINDOW[0],
            "2026-02-01T00:00:00Z",
        )
    )["ok"]
    monitoring.get_alarm_history.assert_called_once()


def test_audit_projection_and_no_unsupported_limit(monkeypatch):
    audit = create_autospec(oci.audit.AuditClient, instance=True)
    item = oci.audit.models.AuditEvent(
        event_type="event",
        data=oci.audit.models.Data(
            event_name="ListInstances",
            resource_id="resource",
            identity=oci.audit.models.Identity(
                principal_id="principal", credentials="secret", ip_address="secret"
            ),
            response=oci.audit.models.Response(status="200"),
            additional_details={"secret": "secret"},
        ),
    )
    audit.list_events.return_value = response([item, item], "cursor")
    monkeypatch.setattr(server, "client", lambda *args: audit)
    result = asyncio.run(
        server.oci_audit_events(COMPARTMENT, REGION, *WINDOW, page_size=1)
    )
    assert result["ok"] and result["truncated"] and result["next_cursor"] is None
    assert "secret" not in str(result)
    assert "limit" not in audit.list_events.call_args.kwargs


def test_metrics_fixed_query_and_global_datapoint_bound(monkeypatch):
    monitoring = create_autospec(oci.monitoring.MonitoringClient, instance=True)
    stream = SimpleNamespace(
        name="CpuUtilization",
        dimensions={"resourceId": "instance"},
        aggregated_datapoints=[SimpleNamespace(timestamp="now", value=1)] * 300,
    )
    monitoring.summarize_metrics_data.return_value = response([stream, stream])
    monkeypatch.setattr(server, "client", lambda *args: monitoring)
    result = asyncio.run(server.oci_metrics(COMPARTMENT, REGION, *WINDOW))
    assert result["ok"] and result["count"] == 500 and result["truncated"]
    details = monitoring.summarize_metrics_data.call_args.args[1]
    assert details.query == "CpuUtilization[5m].mean()"
    assert details.namespace == "oci_computeagent"
    assert not asyncio.run(
        server.oci_metrics(COMPARTMENT, REGION, *WINDOW, resource_id='unsafe"')
    )["ok"]
    assert monitoring.summarize_metrics_data.call_count == 1


@pytest.mark.parametrize("price_key", ["prices", "currencyCodeLocalizations"])
def test_price_is_credential_free_scoped_and_projected(monkeypatch, price_key):
    monkeypatch.setattr(
        server, "auth", lambda *a: pytest.fail("pricing must not authenticate")
    )
    monkeypatch.setattr(
        server,
        "fetch_prices",
        lambda part, currency: {
            "items": [
                {
                    "partNumber": part,
                    "displayName": "Example",
                    "private": "secret",
                    "metricName": "OCPU hour",
                    price_key: [
                        {
                            "currencyCode": "USD",
                            "prices": [{"model": "PAY_AS_YOU_GO", "value": 0.5}],
                        },
                        {
                            "currencyCode": "EUR",
                            "prices": [{"model": "other", "value": 9}],
                        },
                    ],
                }
            ]
        },
    )
    result = asyncio.run(server.oci_price_lookup("B88298"))
    assert result["ok"] and result["count"] == 1
    assert result["items"][0]["value"] == 0.5
    assert "secret" not in str(result)
    assert not asyncio.run(server.oci_price_lookup("../other"))["ok"]


def test_limits_discovery_and_values_share_one_tool(monkeypatch):
    limits = create_autospec(oci.limits.LimitsClient, instance=True)
    limits.list_services.return_value = response([])
    limits.list_limit_values.return_value = response([])
    monkeypatch.setattr(server, "client", lambda *args: limits)
    assert asyncio.run(server.oci_limits(TENANCY, REGION))["ok"]
    assert asyncio.run(server.oci_limits(TENANCY, REGION, service_name="compute"))["ok"]
    limits.list_services.assert_called_once()
    limits.list_limit_values.assert_called_once()


def test_unknown_public_sku_is_empty(monkeypatch):
    monkeypatch.setattr(server, "fetch_prices", lambda *a: {"items": None})
    result = asyncio.run(server.oci_price_lookup("B88298"))
    assert result["ok"] and result["count"] == 0
