---
name: oci-navigator
description: Select the appropriate Oracle cloud or product control plane and automation surface for cross-service architecture, inventory and operations requests.
---

Identify the requested outcome and existing environment, then read
[the operator contract](../../docs/operations.md). Use the smallest relevant set of
domain skills; no mandatory router round-trip is needed for an already clear task.

Consult [the product map](../../docs/oracle-product-map.md) to distinguish OCI
infrastructure, database/application administration, Fusion business APIs and
partner-cloud services. Search [the machine catalog](../../catalog/products.json)
by product/CLI family; it contains navigation units, not a complete product census.

Route identity to `oci-identity`, VM/VCN to `oci-compute-network`, storage to
`oci-storage`, Kubernetes to `oci-oke`, pipelines/functions/artifacts to
`oci-devops`, desired-state infrastructure to `oci-iac`, metrics/logs/incidents to
`oci-observability`, costs/quotas to `oci-finops`, fleet/SQL/26ai to
`oracle-database`, APEX/ORDS to `oracle-apex`, inference/agents/data pipelines to
`oci-ai-data`, defensive posture to `oci-security`, continuity/migration/OS to
`oci-reliability`, SDK application code to `oci-sdk`, and partner-cloud or
enterprise application boundaries to `oracle-multicloud-enterprise`.

Prefer the bundled MCP for its supported reads. Discover other paths from
`catalog/cli.json`, then verify installed help before use. A missing MCP wrapper
does not mean a product lacks an API; an SDK method does not prove entitlement or
availability in the selected region.

For architecture, show the data path, identity boundary, ownership, failure domains,
cost drivers and verification plan. Use current product documentation for regional
features, prices and support limits. State coverage gaps instead of claiming that
a broad diagram is a tested deployment.
