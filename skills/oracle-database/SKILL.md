---
name: oracle-database
description: Operate Oracle Autonomous/Base/Exadata database infrastructure and plan 26ai, vector search and SQL workflows while separating OCI and database privileges.
---

Read [the operator contract](../../docs/operations.md) and the database section of
[the product map](../../docs/oracle-product-map.md). Catalog examples `database-adb`
and `database-versions` inspect hosting resources and available versions.

```bash
oci db autonomous-database list --help
oci db version list --help
oci db system list --help
oci mysql db-system list --help
```

Choose engine, deployment model, actual database release and network path before
writing SQL. OCI provisioning permission does not grant database/schema access.
Connect through a least-privilege database identity; do not default agents to ADMIN.
TLS and wallet-backed mTLS are different connection modes. Treat wallets and
connection artifacts as secrets and verify driver/version requirements.

For database MCP, distinguish SQLcl local stdio, OCI Database Tools and supported
ORDS endpoints. Inspect exposed tools and database grants before enabling them.
Arbitrary SQL cannot be made read-only by checking the first word of the query.
This package's OCI MCP does not execute SQL.

For 26ai vector work, verify actual release/deployment support, dimension, element
format, embedding model and distance metric. Model changes may require re-embedding.
Separate exact versus approximate search, index build/storage and vector-memory
cost. Evaluate retrieval against representative queries, including lexical error
codes; presentation slides are not release-specific SQL validation.

For backups, patching or migration, document RPO/RTO, dependencies, recovery tests,
license assumptions and downtime. Verify SQL/application health after control-plane
completion. Never describe an untested backup or failover plan as demonstrated DR.

[Database documentation](https://docs.oracle.com/en/database/),
[Database MCP choices](https://www.oracle.com/mcp/)
