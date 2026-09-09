# Select AI and NL2SQL

Select AI is an Autonomous feature, not a guarantee of an on-prem Free installation. AI profiles use DBMS_CLOUD_AI; profile and credential creation are writes. Record permitted tables, approved provider/egress and session identity before generating anything.

Prefer SELECT AI showsql for a separately authorized generation request, then review the proposed statement. It does not execute the generated SQL, but it can still send schema/prompt data to a billable model. SELECT AI without an action defaults to runsql and executes generated SQL under the session privileges. Neither is part of the read-only preflight.

Do not put credential creation, user grants, arbitrary PL/SQL or tool definitions into an agent's callable SQL surface. Select AI Agent tools and in-database MCP permissions need the same database-user boundary as SQLcl. This workflow remains [unverified]; no provider call was made.
