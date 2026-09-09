# Dedicated clusters

Pretrained dedicated hosting uses supported logical cluster shapes; imported-model hosting may expose raw GPU capacity. A Compute GPU name is not automatically a valid dedicated AI cluster unit shape.
Before any create/update proposal, establish region/model support, unit count, endpoint capacity, limits, minimum commitment and idle billing from current documentation and pricing. Dedicated capacity is not assumed to scale to zero. Fine-tuning and hosting are separate purposes; wait for their own work requests and lifecycle states.
A rollout needs test traffic, quality/latency comparison, old endpoint retention and a reversible client-routing change. Deleting a cluster is not an instant cost-free rollback and may require removing dependent endpoints first. No capacity was provisioned here.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| SignUpRequired | Service not enabled for the tenancy (common on Gen-AI, some ADB features) | id 12 [unverified] |
| InvalidParameter | A body/query parameter value is invalid or malformed | id 2 [unverified] |
