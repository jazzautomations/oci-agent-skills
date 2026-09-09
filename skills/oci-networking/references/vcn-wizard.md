# VCN construction
Source: research/04c Networking.
Plan non-overlapping CIDRs before creation. The wizard expands to VCN, gateways, route tables, subnet security, then subnets. A route to an internet gateway, a public IP and permitting security rules are separate prerequisites for inbound access.
For private egress use NAT; for supported Oracle services use a service gateway. Discover the region's service ID and CIDR label; its route uses destinationType SERVICE_CIDR_BLOCK.
Record each created ID locally and reverse dependencies for rollback. Do not delete a pre-existing VCN, default route table or shared gateway as cleanup.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| RequestException | Bad region, blocked egress, corporate proxy | id 121 [unverified] |
| Conflict | Overlapping CIDR with a peered VCN | id 124 [unverified] |
