---
name: oracle-multicloud-enterprise
description: Map Oracle Database multicloud and enterprise products to their actual subscription, API, identity and operational ownership boundaries.
---

Read [the operator contract](../../docs/operations.md),
[product map](../../docs/oracle-product-map.md) and
[catalog/products.json](../../catalog/products.json). This skill supports discovery
and architecture; it does not claim tested Fusion, NetSuite or partner-cloud integrations.

For Database@Azure/@AWS/@Google Cloud, establish the exact contracted offering,
partner account, Oracle subscription, supported region, database type, networking,
identity and billing. Native OCI API availability is not proof of partner-cloud
feature parity. Interconnect availability is distinct from a Database@ deployment.

For Fusion ERP/HCM/SCM/CX or NetSuite, select the application's supported API and
business-role model. OCI IAM does not grant business-record access. Likewise,
WebLogic, Oracle Linux, Java Management, GraalVM, Analytics and Integration have
product/version-specific lifecycle and support boundaries. Find the exact product
docs rather than inventing CLI commands for a product name.

Produce a responsibility matrix: infrastructure, application/data, networking,
identity, billing, backup and incident response. Show where data crosses accounts,
clouds or jurisdictions and which side owns the relevant endpoint and policy.

Verify current entitlement, regional availability, licensing and commercial terms
before estimating or provisioning. If access is unavailable, finish the concrete
architecture/API plan and state which verification requires that environment.
Do not create a paid subscription or enable a cross-account trust during discovery.

[Multicloud](https://docs.oracle.com/en-us/iaas/Content/multicloud/home.htm),
[Oracle documentation](https://docs.oracle.com/en/)
