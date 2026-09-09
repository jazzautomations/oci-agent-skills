# Load balancing
Source: research/04c LB; research/09b.
LB is an HTTP/TLS-aware service; NLB handles transport-layer forwarding. Select from required protocol, source-IP preservation and TLS termination rather than assuming interchangeability.
Read backend-set health, listener protocol/port and health-check configuration. Permit health probes from the LB network to the actual backend health port; test whether the application listens and returns the expected path/status.
LB writes return work requests. A successful request submission does not establish backend health. Preserve the former backend set/listener configuration before proposing changes. Subnet requirements vary by regional versus legacy AD placement; confirm the current service model.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| RequestException | Bad region, blocked egress, corporate proxy | id 121 [unverified] |
| `SSLError` / `CERTIFICATE_VERIFY_FAILED` | Corporate MITM proxy | id 122 [unverified] |
