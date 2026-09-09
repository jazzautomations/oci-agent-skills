# SQLcl MCP and read-only users

SQLcl MCP is a client-side server for an existing Oracle connection, not the OCI database control plane. Use SQLcl 25.2+ with the documented JRE and pin the tested version. Curate the saved-password connections in ~/.dbtools: every available connection is within the model's reach. Do not save ADMIN beside an agent connection.

The default sql -mcp restriction is level 4, blocking host commands and scripts. Restrict levels do NOT block DML/DDL issued through run-sql. Do not call a connection read-only based on -R. A project-local MCP declaration can use {"command":"/opt/sqlcl/bin/sql","args":["-mcp"]}; substitute an actual trusted installation path. If script execution is required, separately review -R 1; do not ship unrestricted -R 0.

DBA setup proposal [unverified, never executed here]: create a dedicated user with CREATE SESSION and READ on specific approved tables, no role inheritance, no ANY privileges, no DDL privileges, no exposed definer-rights procedures, and no data outside the approved row policy. READ is narrower than SELECT because it excludes SELECT FOR UPDATE. Quotas/profile limits do not replace privilege control. Keep credentials outside repo/config examples.

Run readonly_user.sql as the agent identity to inspect session grants. A DBA must also inspect inherited/public/schema grants and accessible executable routines. negative_test.sql is a read-only risk report, not a write test. To prove denials, a DBA must separately prepare disposable sentinel objects in an isolated clone and test INSERT/CREATE/DROP from the exact agent identity. Expected denials include ORA-01031/ORA-00942; any unexpected success fails certification and requires cleanup. Never do this against production: DDL commits and cannot be made safe by ROLLBACK.

SQLcl uses MODULE/ACTION and DBTOOLS$MCP_LOG for attribution. Verify logging behavior and retention for the installed version without granting extra privileges just to enable it. No SQLcl process or negative mutation test was run here.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| `ORA-01017: invalid (username/password\\|credential).*logon denied` | Wrong password, or the wallet belongs to a *different* ADB | id 100 [unverified] |
| `401 Unauthorized` on an ORDS REST endpoint | Missing OAuth client / privilege mapping | id 109 [unverified] |
