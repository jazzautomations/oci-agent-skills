---
name: oracle-apex
description: Build and operate Oracle APEX applications and ORDS/SQLcl delivery, separating workspace, schema, application and database hosting lifecycle.
---

Read [the operator contract](../../docs/operations.md) and APEX/ORDS guidance in
[the product map](../../docs/oracle-product-map.md). First inspect the actual APEX,
ORDS, SQLcl and database versions and whether deployment is managed or self-hosted.

Hosting discovery can use catalog example `database-adb`. Application inspection
must use authorized APEX/SQLcl/ORDS interfaces; listing an Autonomous database is
not an APEX application smoke test. This package does not include SQL credentials.

Track workspace, parsing schema, application ID, authentication scheme,
authorization rules, REST modules and environment-specific substitutions. Plan
schema migrations and application export/import separately. Read the installed
SQLcl help for export and deployment syntax rather than guessing flags.

Keep application exports, schema migrations and release notes in version control.
Exclude workspace credentials, wallets and exported secrets. Review application-ID
collisions, supporting-object scripts and environment URLs before import. Importing
an application may execute supporting SQL; it is not merely copying UI files.

For ORDS, verify pool/schema mapping, auth and authorization, TLS/proxy behavior,
connection limits and endpoint health. Exposing a REST module or database MCP
changes the data-access surface and needs explicit endpoint and privilege scope.

Validate login, authorization boundaries, representative pages/forms, REST contracts
and schema compatibility after deployment. A successful import is not a user-flow
test. Preserve the previous app export and a separate data/schema rollback strategy.

[APEX docs](https://docs.oracle.com/en/database/oracle/application-express/),
[ORDS](https://www.oracle.com/database/technologies/appdev/rest.html)
