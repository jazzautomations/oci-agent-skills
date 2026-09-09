# DNS
Source: research/09b §18.
Distinguish GLOBAL public zones from PRIVATE zones and views. A private zone can exist without being visible from the querying VCN: inspect resolver attached views and endpoints.
Hybrid DNS needs forwarding/listening endpoint direction plus security and routing in both networks. Test from the failing client's resolver path; a public resolver answer does not verify private resolution.
Record zone, view and resolver IDs independently. An RRset replacement must retain the complete intended record set and TTLs. Preserve the prior set and ETag before proposing an update.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| RequestException | Bad region, blocked egress, corporate proxy | id 121 [unverified] |
| NotAuthorizedOrNotFound | Deliberate ambiguity: missing resource OR missing policy OR wrong region OR wrong compartment | id 13 [unverified] |
