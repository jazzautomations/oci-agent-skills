# ORDS ownership and REST access

On ADB, ORDS is managed and pool settings are not user-tunable. Read actual connection URLs and tool enablement. A stopped/restarting ADB or HTTP rate limits can explain failure even when an app exists. Customer-managed ORDS support depends on workload; do not apply that pattern to APEX Service automatically.

AutoREST exposes CRUD; auth flags do not make it GET-only. For read-only tools use a separately approved module containing fixed projected SQL, bind parameters, bounded pages and explicit role/OAuth privileges. Never assume browser page items are set in an ORDS session.

DEFINE_MODULE and DEFINE_TEMPLATE can replace existing child definitions. Capture complete metadata before any change; the URL mapping cannot simply be renamed while REST-enabled. Inspect schema alias and privilege mapping for 401, app deployment for 404, and lifecycle/pool state for 503. ADB database-user authentication maps to that user's schema URL space. Raw agent SQL belongs to oracle-db-sql-access.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| `503 Service Unavailable` from `/ords/` | ADB stopped/restarting, or ORDS pool exhausted | id 107 [unverified] |
| `401 Unauthorized` on an ORDS REST endpoint | Missing OAuth client / privilege mapping | id 109 [unverified] |
