# Reachability
Source: research/04c Networking/LB; research/09b §§16–19.
Trace client DNS → source route → gateway/peering → destination route → NSG/security list → host firewall → listening process. Compare TCP refused with a timeout; neither alone proves an OCI security-rule failure.
NAT provides outbound connectivity, not unsolicited ingress. An allowed-public-IP subnet is insufficient without an internet route and assigned public address.
Check both security lists and NSGs for unexpected exposure. Avoid widening source CIDRs as a diagnostic step. Capture a specific source, destination, protocol, port and time window before proposing a rule.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| RequestException | Bad region, blocked egress, corporate proxy | id 121 [unverified] |
| Conflict | Overlapping CIDR with a peered VCN | id 124 [unverified] |
