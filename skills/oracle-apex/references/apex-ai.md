# APEX Assistant and AI providers

Inspect the installed APEX version before choosing provider features. A Generative AI Service is workspace-scoped, identified by a Static ID and backed by a Web Credential. Only one service can be Used by App Builder. Create service objects through supported Builder/import flows; do not invent a public create-service PL/SQL API.

Keep credentials server-side with allowed URL restrictions; exports omit their secrets. Retarget environment-specific remote servers after a reviewed import. APEX_AI needs a valid application session. No session creation or inference is part of this skill's read-only script.

APEX 26.1 AI Agents have tool definitions and parameters visible in APEX_AI_AGENTS, APEX_AI_AGENT_TOOLS and APEX_AI_AGENTS_TOOL_PARAMS. Server/client code tools can cause side effects. Approval-gated tools have frontend restrictions and are not interchangeable with backend APEX_AI calls. JSON response validation depends on DB support; validate explicitly on 19c.

Bound token budgets and tool round trips; treat model code and tool results as untrusted. Generated SQL/code requires review before deployment. Provider calls are billable and can disclose prompt data. APEX_AI execution is [unverified] here.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| `404 Not Found` on `/ords/<schema>/...` or `Request could not be processed` | App/workspace not deployed in *that* ADB, or the schema is not REST-enabled | id 106 [unverified] |
| `503 Service Unavailable` from `/ords/` | ADB stopped/restarting, or ORDS pool exhausted | id 107 [unverified] |
