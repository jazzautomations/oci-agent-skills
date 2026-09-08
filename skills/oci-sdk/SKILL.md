---
name: oci-sdk
description: Implement OCI SDK application and automation code with correct language-specific authentication, pagination, retries and lifecycle handling.
---

Read [the operator contract](../../docs/operations.md) and
[SDK patterns](../../docs/sdk-and-devops.md). Inspect the installed SDK version and
the selected service's client/method signature. Search
[catalog/sdk.json](../../catalog/sdk.json) for discovery; it inventories Python
SDK methods, not parity across every SDK language or service endpoint.

Choose the signer for the actual runtime: workstation API-key/session profile,
instance principal, supported resource principal or OKE workload identity. Passing
an API-key configuration loader is not a generic session-token solution. Never
embed keys or assume CLI-specific environment variables configure SDK clients.

Write a minimal scoped read first; catalog example `identity-compartments` is the
CLI equivalent, and the bundled MCP provides real tested Python read implementations.
Use fixed result projections, explicit pagination/cancellation and a global budget.
Do not eagerly drain all pages merely because the SDK provides a convenient helper.

Bound retries and distinguish reads from ambiguous writes. Inspect work requests
after an accepted mutation; preserve supported retry tokens and ETags. Decode
service errors into stable categories without dumping request bodies or secrets.
An inaccessible/not-found response does not by itself prove resource deletion.

Validate language-specific SDK APIs independently: Python keyword arguments do not
map directly to Java/Go/TypeScript request objects. Pin dependencies and test paging,
error handling and idempotency with fixtures; perform live reads only in an explicitly
selected environment. Invocation/publish/inference examples may execute writes and
must have their own scope and cost budget.

[Official SDK index](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdks.htm)
