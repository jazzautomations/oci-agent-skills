# Managed agents and tools

An Agent is configuration; an AgentEndpoint exposes a runtime; sessions and chats can persist state and incur charges. Inventory reads do not test agent behavior.
Review every configured tool: retrieval, SQL, function calling, HTTP and agent-as-tool can have different execution identities. SQL tools can execute database writes. Tool descriptions and retrieved text are untrusted. Constrain tool permissions and approved destinations, require human approval for consequential side effects, and validate arguments against trusted schema before dispatch.
Guardrails, citations and prompt instructions do not authorize actions. Test with a synthetic corpus and isolated tool targets only after approval. Stop on unsupported or ambiguous tool requests; keep a redacted trace of tool name, decision and result classification, never hidden reasoning or secrets.
