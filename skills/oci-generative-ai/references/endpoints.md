# Endpoint routing

Distinguish model identifiers, dedicated inference endpoints and managed Agent endpoints. Control plane generative-ai, inference generative-ai-inference and agent-runtime use different APIs. Pass region and let the CLI/SDK resolve realm endpoints; never construct commercial hostnames for sovereign realms.
Check endpoint lifecycle and underlying cluster readiness. Private access adds DNS, routing, service availability and IAM prerequisites; an ACTIVE endpoint does not prove client reachability. OpenAI-compatible or Responses interfaces have different request and streaming shapes; do not paste their payload into ChatDetails. API keys and stored responses are sensitive; do not enumerate values or create keys as a probe.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| SignUpRequired | Service not enabled for the tenancy (common on Gen-AI, some ADB features) | id 12 [unverified] |
| InvalidParameter | A body/query parameter value is invalid or malformed | id 2 [unverified] |
