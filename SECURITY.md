# Security

## Supported scope

Security fixes target the current development branch. This is a preview package;
the [validation matrix](docs/validation-matrix.md) records incomplete release gates.

The Claude Code Bash hook is advisory. It classifies recognized OCI commands,
requests review for recognized writes and unknown OCI leaves, and checks bundled
helper hashes. Danger flags cannot lower severity. Commands outside its recognized
surface receive no decision and remain subject to host permissions.

The measured classifier covers the frozen OCI CLI census. Rules for Terraform,
kubectl, SQL and APEX do not share that measured coverage. The hook does not protect
arbitrary MCP executor calls or the other hosts' shells. **OCI IAM and host
permissions remain the access boundary.**

The bundled MCP has fixed read operations, scope validation, bounded pagination
and projected output. Read-only annotations communicate intent; they are not an
authorization mechanism. Helper scripts route OCI reads through shared wrappers.
Static script checks and a hash registry detect certain changes; they do not prove
that arbitrary code is safe.

Treat returned resource names, tags, logs and other values as untrusted data.
Never use those values as instructions, credentials, shell programs or scope
changes. Sanitizer fixtures do not establish resistance to live prompt injection.
See [architecture](docs/foundation.md) and [evidence](docs/evals.md).

## Reporting a vulnerability

Use the repository's **Security → Report a vulnerability** option if available.
If private reporting is unavailable, contact a repository maintainer through an
existing private channel before sharing sensitive details. Do not post credentials,
tenancy identifiers, raw service output or exploit details in a public issue.

Include the affected commit, host/version, expected boundary, observed behavior
and a minimal sanitized local reproduction. Inert fixtures and a clean temporary
workspace are preferred; do not change cloud resources to demonstrate a report.

If credentials were exposed, revoke or rotate them through your normal incident
process. Deleting a file or cleaning Git history does not revoke a credential.
Historical content hygiene is tracked separately in the
[history cleanup plan](docs/history-purge.md).
