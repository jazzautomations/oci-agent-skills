# NSGs and security lists
Source: research/04c Networking.
Rules are additive: a permit in either subnet security lists or VNIC NSGs can allow traffic. NSGs attach to VNICs; a security list covers its subnet. Stateful rules track return flows; stateless rules require an explicit return path.
Security-list ingress/egress updates and route-table updates replace arrays. Read the complete current document, merge locally, review the diff and use its ETag with if-match. On NoEtagMatch, read again and review a new merge.
merge_rules.py accepts two local JSON arrays, preserves order and removes exact duplicates. It never writes OCI. Its stdout is a sensitive proposal; redirect locally and do not commit it. NSG incremental add/update/remove verbs are distinct from full-array replacement.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| NoEtagMatch | Optimistic-concurrency `if-match` stale | id 23 [unverified] |
| NotAuthorizedOrNotFound | Deliberate ambiguity: missing resource OR missing policy OR wrong region OR wrong compartment | id 13 [unverified] |
