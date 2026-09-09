# Choose the database MCP plane

Three choices have different authorization boundaries. OCI database MCP/CLI operates infrastructure handles. SQLcl MCP executes SQL under saved database credentials. Autonomous in-database MCP exposes registered Select AI Agent tools; it is not a universal execute_sql endpoint.

Autonomous MCP enablement uses the adb$feature free-form tag, so turning it on is an OCI update and is never done here. Preserve existing tags in any separately reviewed proposal. Public/private endpoint reachability, OAuth or bearer-token lifetime and per-database tool grants must be checked independently. Obtain documented endpoints from the selected service; do not manufacture realm hosts or log tokens. Disabling the feature stops new sessions; it does not necessarily cancel in-flight work.

The dbtools MCP server can POST arbitrary statementText through ORDS. Its SELECT-based retry logic is not a read-only execution guard. Report-creation helpers and ragify_column can write. Prefer fixed SQL with typed bind parameters and an independently restricted database identity. Tool descriptions, MCP readOnlyHint and prompts do not enforce database permissions. Database Tools connection objects reference secrets; metadata access must not become secret-bundle retrieval. All MCP end-to-end behavior remains [unverified].
