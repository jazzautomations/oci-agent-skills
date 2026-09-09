# Pages, session state and authorization

Choose a component for the user task: Interactive Report for exploration, Interactive Grid for controlled tabular editing, Faceted Search/Smart Filters for narrowing a result set, and forms for validated single-record changes. Universal Theme provides the layout; preserve stable component Static IDs in source control.

Check the processing order: submit → computations/validations → processes → branches, including conditions and authorization on each server-side action. Dynamic Actions can change browser state without persisting it to the server. Explicitly submit required page items for Ajax calls and never use an ORDS request as if it shared browser session state.

Apply authentication, authorization and row filtering on the server; hiding a button is not authorization. Enable session state protection, output escaping and bind variables. An editable grid or form needs a reviewed DML process and lost-update handling. Automations/email/background jobs can run after a deployment and need separate scope review.

For APEXlang generation use a pinned, reviewed Oracle grammar/toolchain, then offline validation. Do not call internal wwv_flow_imp_page APIs from hand-written automation. After an approved deployment verify login, roles, representative pages, validation failures and REST contracts in a browser; a successful import is not a user-flow test.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| `404 Not Found` on `/ords/<schema>/...` or `Request could not be processed` | App/workspace not deployed in *that* ADB, or the schema is not REST-enabled | id 106 [unverified] |
| `503 Service Unavailable` from `/ords/` | ADB stopped/restarting, or ORDS pool exhausted | id 107 [unverified] |
