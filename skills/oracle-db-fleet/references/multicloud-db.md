# Database at Azure, AWS or Google

Keep two planes apart: multicloud owns OCI anchors, subscriptions and network mappings; dbmulticloud owns database connectors, partner key vaults and blob mounts. Neither replaces partner marketplace ordering or partner IAM. Record the purchase cloud, physical region pairing, OCI resource type and which console owns the next step.

Read the actual database noun after identifying its OCI anchor; never substitute a partner resource ID for an OCI OCID. Validate private DNS, interconnect routes, partner egress and key permissions on both sides. Preserve the agreed RPO/RTO and data residency during a role-transition proposal. A switchover and failover are different recovery decisions, even when the Oracle engine is identical. This tenancy has no multicloud DB; partner paths remain [unverified].

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| ExternalServerIncorrectState | A customer-owned server (DB agent, on-prem host, Exadata) is unreachable/misbehaving | id 19 [unverified] |
| `ORA-12541: TNS:no listener` | Wrong host/port, or the ADB is **STOPPED** | id 101 [unverified] |
