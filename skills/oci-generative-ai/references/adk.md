# OCI ADK

The Python ADK is distributed with the OCI SDK extra oci[adk], with imports under oci.addons.adk; pin a compatible version and use its shipped examples. Source is the Oracle OCI SDK repository, not an assumed standalone agent-development-kit repository.
ADK client orchestration is distinct from configuring a managed service. A run can create sessions, invoke inference and execute local Python tools. Do not install or run an example merely to inspect it. Bind tools explicitly, use least-privilege identities, cap steps/tokens/retries, and require approval before side effects. Keep ordinary deterministic API logic outside the model loop.
No ADK runtime was exercised. chat_min.py only prepares JSON and does not import ADK or OCI.
