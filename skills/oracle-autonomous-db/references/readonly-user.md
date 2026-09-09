# Read-only database identity

An agent connection must use a dedicated database user, preferably on a sanitized read-only replica. CREATE SESSION plus explicit READ on approved tables is narrower than SELECT: READ excludes SELECT FOR UPDATE and LOCK TABLE. Avoid CONNECT, RESOURCE, DWROLE, ANY privileges and executable definer-rights packages. QUOTA 0 alone is not a read-only guarantee.

A DBA must separately review user creation, grants, role inheritance, schema grants, quotas, public grants and resource-profile enforcement. Do not run setup SQL in this repository. Use oracle-db-sql-access for the privilege audit and isolated negative-test procedure; its scripts only inspect metadata. A successful SELECT does not prove writes are denied.

Set module/action for attribution, cap client fetches and pool concurrency, and arrange statement deadlines. CPU/resource profile limits require the applicable database enforcement configuration. No SQL privilege configuration was live-verified.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| `ORA-01017: invalid (username/password\\|credential).*logon denied` | Wrong password, or the wallet belongs to a *different* ADB | id 100 [unverified] |
| `ORA-28000: The account is locked; login denied\.?` | Repeated bad logins locked `ADMIN`, or the ADB was stopped/restored | id 99 [unverified] |
