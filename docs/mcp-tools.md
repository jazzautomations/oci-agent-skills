# MCP tool reference

[Documentation](README.md) · [Skills catalog](skills.md)

Generated from the bundled server's `list_tools()` schemas without loading OCI credentials or making service calls. Regenerate with `uv run --frozen --project runtime python scripts/doc-gen/catalogs.py`.

**15 tools**, all annotated read-only and non-destructive. `oci_price_lookup` uses public pricing; the other tools require OCI authentication. Annotations describe intent; fixed operation dispatch, explicit scope and IAM enforce the supported access.

See [runtime configuration](../runtime/README.md) for authentication, scope, timeouts, pagination and output envelopes. No generic CLI, SQL or SDK executor is exposed.

| Tool | Description | Read-only | Required arguments |
|---|---|---|---|
| [oci_alarm_status](#oci-alarm-status) | List alarm status; an alarm ID and bounded timestamps select its history. | true | `compartment_id`, `region` |
| [oci_audit_events](#oci-audit-events) | Read at most one Audit page over a window of up to 24 hours; excludes payloads. | true | `compartment_id`, `region`, `start_time`, `end_time` |
| [oci_buckets](#oci-buckets) | Read bucket metadata only; resolves namespace internally. Never lists or downloads objects. | true | `compartment_id`, `region` |
| [oci_compartments](#oci-compartments) | Discover child compartments. Subtree reads require a permitted subtree scope. | true | `compartment_id`, `region` |
| [oci_cost_summary](#oci-cost-summary) | Costs by 1–4 dimensions; UTC end exclusive, ≤31 days. Descendant/region scope is explicit; depth only groups. IAM may omit rows; currencies remain separate. | true | `compartment_id`, `region`, `start_date`, `end_date` |
| [oci_instances](#oci-instances) | Read one page of compute instance summaries; excludes metadata, tags, addresses and user data. | true | `compartment_id`, `region` |
| [oci_limit_services](#oci-limit-services) | List limit services for the authenticated tenancy. | true | `tenancy_id`, `region` |
| [oci_limit_values](#oci-limit-values) | List configured limit values for one service; limits do not measure capacity. | true | `tenancy_id`, `region`, `service_name` |
| [oci_metrics](#oci-metrics) | Read fixed compute-agent metric templates; max 24 hours and 500 datapoints. | true | `compartment_id`, `region`, `start_time`, `end_time` |
| [oci_network_inventory](#oci-network-inventory) | Read one page of VCN, subnet or NSG summaries; does not fetch rules, routes or traffic. | true | `compartment_id`, `region` |
| [oci_price_lookup](#oci-price-lookup) | Look up one public Oracle SKU without credentials; list prices are not a quote. | true | `part_number` |
| [oci_regions](#oci-regions) | List the authenticated tenancy's region subscriptions; no cloud writes. | true | `tenancy_id`, `region` |
| [oci_resource_search](#oci-resource-search) | Read resource-search summaries in exactly one compartment. No caller-supplied query language; search is eventually consistent and excludes unsupported types. | true | `compartment_id`, `region` |
| [oci_whoami](#oci-whoami) | Inspect active identity, scope and region subscriptions; never key material. | true | None |
| [oci_work_requests](#oci-work-requests) | List common work requests, or inspect one request's status, errors or logs. | true | `compartment_id`, `region` |

## oci-alarm-status

`oci_alarm_status` — List alarm status; an alarm ID and bounded timestamps select its history.

| Argument | Type | Required | Default |
|---|---|---|---|
| `compartment_id` | string | yes | — |
| `region` | string | yes | — |
| `alarm_id` | string / null | no | None |
| `start_time` | string / null | no | None |
| `end_time` | string / null | no | None |
| `page_size` | integer | no | 50 |
| `cursor` | string / null | no | None |

## oci-audit-events

`oci_audit_events` — Read at most one Audit page over a window of up to 24 hours; excludes payloads.

| Argument | Type | Required | Default |
|---|---|---|---|
| `compartment_id` | string | yes | — |
| `region` | string | yes | — |
| `start_time` | string | yes | — |
| `end_time` | string | yes | — |
| `page_size` | integer | no | 50 |
| `cursor` | string / null | no | None |

## oci-buckets

`oci_buckets` — Read bucket metadata only; resolves namespace internally. Never lists or downloads objects.

| Argument | Type | Required | Default |
|---|---|---|---|
| `compartment_id` | string | yes | — |
| `region` | string | yes | — |
| `page_size` | integer | no | 50 |
| `cursor` | string / null | no | None |

## oci-compartments

`oci_compartments` — Discover child compartments. Subtree reads require a permitted subtree scope.

| Argument | Type | Required | Default |
|---|---|---|---|
| `compartment_id` | string | yes | — |
| `region` | string | yes | — |
| `page_size` | integer | no | 50 |
| `cursor` | string / null | no | None |
| `include_subtree` | boolean | no | False |

## oci-cost-summary

`oci_cost_summary` — Costs by 1–4 dimensions; UTC end exclusive, ≤31 days. Descendant/region scope is explicit; depth only groups. IAM may omit rows; currencies remain separate.

| Argument | Type | Required | Default |
|---|---|---|---|
| `compartment_id` | string | yes | — |
| `region` | string | yes | — |
| `start_date` | string | yes | — |
| `end_date` | string | yes | — |
| `page_size` | integer | no | 50 |
| `cursor` | string / null | no | None |
| `compartment_depth` | integer | no | 1 |
| `include_descendants` | boolean | no | False |
| `all_regions` | boolean | no | False |
| `group_by` | array | no | ['service', 'compartmentId'] |

## oci-instances

`oci_instances` — Read one page of compute instance summaries; excludes metadata, tags, addresses and user data.

| Argument | Type | Required | Default |
|---|---|---|---|
| `compartment_id` | string | yes | — |
| `region` | string | yes | — |
| `page_size` | integer | no | 50 |
| `cursor` | string / null | no | None |

## oci-limit-services

`oci_limit_services` — List limit services for the authenticated tenancy.

| Argument | Type | Required | Default |
|---|---|---|---|
| `tenancy_id` | string | yes | — |
| `region` | string | yes | — |
| `page_size` | integer | no | 50 |
| `cursor` | string / null | no | None |

## oci-limit-values

`oci_limit_values` — List configured limit values for one service; limits do not measure capacity.

| Argument | Type | Required | Default |
|---|---|---|---|
| `tenancy_id` | string | yes | — |
| `region` | string | yes | — |
| `service_name` | string | yes | — |
| `page_size` | integer | no | 50 |
| `cursor` | string / null | no | None |

## oci-metrics

`oci_metrics` — Read fixed compute-agent metric templates; max 24 hours and 500 datapoints.

| Argument | Type | Required | Default |
|---|---|---|---|
| `compartment_id` | string | yes | — |
| `region` | string | yes | — |
| `start_time` | string | yes | — |
| `end_time` | string | yes | — |
| `template` | string | no | 'cpu_utilization' |
| `resource_id` | string / null | no | None |

## oci-network-inventory

`oci_network_inventory` — Read one page of VCN, subnet or NSG summaries; does not fetch rules, routes or traffic.

| Argument | Type | Required | Default |
|---|---|---|---|
| `compartment_id` | string | yes | — |
| `region` | string | yes | — |
| `resource` | string | no | 'vcns' |
| `page_size` | integer | no | 50 |
| `cursor` | string / null | no | None |

## oci-price-lookup

`oci_price_lookup` — Look up one public Oracle SKU without credentials; list prices are not a quote.

| Argument | Type | Required | Default |
|---|---|---|---|
| `part_number` | string | yes | — |
| `currency` | string | no | 'USD' |

## oci-regions

`oci_regions` — List the authenticated tenancy's region subscriptions; no cloud writes.

| Argument | Type | Required | Default |
|---|---|---|---|
| `tenancy_id` | string | yes | — |
| `region` | string | yes | — |
| `page_size` | integer | no | 100 |

## oci-resource-search

`oci_resource_search` — Read resource-search summaries in exactly one compartment. No caller-supplied query language; search is eventually consistent and excludes unsupported types.

| Argument | Type | Required | Default |
|---|---|---|---|
| `compartment_id` | string | yes | — |
| `region` | string | yes | — |
| `page_size` | integer | no | 50 |
| `cursor` | string / null | no | None |

## oci-whoami

`oci_whoami` — Inspect active identity, scope and region subscriptions; never key material.

| Argument | Type | Required | Default |
|---|---|---|---|

## oci-work-requests

`oci_work_requests` — List common work requests, or inspect one request's status, errors or logs.

| Argument | Type | Required | Default |
|---|---|---|---|
| `compartment_id` | string | yes | — |
| `region` | string | yes | — |
| `work_request_id` | string / null | no | None |
| `page_size` | integer | no | 50 |
| `cursor` | string / null | no | None |
| `detail` | string | no | 'summary' |
