---
name: oci-finops
description: Analyze OCI reported costs, budgets, quotas and capacity without confusing billing, entitlement and resource availability.
---

Read [the operator contract](../../docs/operations.md). Use `oci_cost_summary`,
`oci_limit_services` and `oci_limit_values` for bounded reads. Catalog examples:
`cost-usage`, `cost-budgets`, `limits-services`, `limits-values`.

```bash
oci usage-api usage-summary request-summarized-usages --help
oci budgets budget budget list --help
oci limits value list --help
oci limits resource-availability get --help
```

Set explicit UTC period, exclusive end, region, compartment and currency. Usage
reports can lag and child compartments may be excluded. Do not add amounts across
currencies or imply that a partial page is the invoice total. Budgets are alerts,
not universal hard spending caps. Quotas, limits and physical capacity differ.

For changes over time, compare equal completed baseline/current windows with the
same compartment, region, currency and aggregation; account for reporting lag.
The catalog's CLI `cost-usage` example is tenancy-wide across resource regions;
its API endpoint region is not a billing filter. Use the runtime's explicit filters
or a verified Usage API filter when the requested analysis is narrower.
The MCP groups costs by service, so it can locate a service-level increase but
cannot prove which resource or change caused it. Follow with scoped billing
dimensions, workload metrics and change history before asserting a root cause.

For a future estimate, identify current region/SKU/meter/currency, utilization,
storage, network transfer, logs, support and licensing assumptions. Retrieve current
official rates; never reuse cached prices as current. A free allowance on Compute
does not make a whole architecture free, and availability is not guaranteed.

Rightsizing requires metric history and workload constraints, not shape price alone.
Distinguish a recommendation from a stop/resize commitment. Cost-report exports and
FOCUS/showback pipelines need explicit data access and validation of billing fields.

Before requesting a limit increase, verify the exact service/limit/AD, current
allocation and required capacity. Creating a support request is an external write;
prepare evidence first and submit only when in scope.

[Cost analysis](https://docs.oracle.com/en-us/iaas/Content/Billing/Concepts/costanalysisoverview.htm),
[Price list](https://www.oracle.com/cloud/price-list/)
