# Functions
Source: research/09a §21; research/10a §3.11.
A Functions application selects compartment, subnets and processor architecture; each function selects an image digest, memory and timeout. fn deploy builds, pushes and changes OCI resources, so it is a proposal only. No function was invoked here: an invocation can mutate downstream systems even if the CLI verb sounds like a read.
Use the region's Fn context and registry namespace. Match the image platform to the application's architecture; verify the digest exists and can be pulled. Allow private subnet egress to the required OCI services through the reviewed gateway/security path.
For Python, use the FDK handler shape handler(ctx, data: io.BytesIO = None), return an FDK response with the intended media type, and handle missing or malformed payloads. Initialize reusable SDK clients outside the handler when safe. Use the resource principal signer and resource-principal policies rather than shipping an API key in an image.
[unverified] Fn CLI and FDK package behavior were not executed here. Distinguish cold-start latency, application timeout, synchronous request limits and detached execution. A high timeout does not repair an unreachable dependency. Keep provisioned concurrency and its cost explicit.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| RelatedResourceNotAuthorizedOrNotFound | An OCID **inside the request body** (subnet, image, vault key, NSG) is missing or unreadable by you | id 7 [unverified] |
| IncorrectState | Resource is mid-transition (`PROVISIONING`, `TERMINATING`, `UPDATING`) | id 18 [unverified] |
