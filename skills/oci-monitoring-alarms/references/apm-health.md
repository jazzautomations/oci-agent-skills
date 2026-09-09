# APM and Health Checks
Source: research/09b §§9,12.
APM domains, application traces and synthetic monitors answer different questions. Trace/span data can contain request headers, identities and secrets; query only a bounded incident window and redact payloads. Public and private data keys have different privileges; never emit a private data key.
Health Checks probes test an external endpoint from chosen vantage points. Confirm method, path, TLS verification, expected status and network exposure. Do not treat one healthy probe as proof of internal dependency health.
Synthetic browser scripts can log in, submit forms or modify applications. Creating or running a monitor is not a read-only test. [unverified] No synthetic monitor, probe or APM configuration was created or executed here. Review target ownership, credentials and side effects before proposing one.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| InvalidParameter | A body/query parameter value is invalid or malformed | id 2 [unverified] |
| TooManyRequests | Per-user/per-tenancy throttle | id 26 [unverified] |
