# AD and fault-domain spread

Discover availability domains in the selected tenancy/region; names are tenancy-specific. Do not assume every region has three ADs. Fault domains divide hardware failure/maintenance groups inside one AD, not independent regions.
Group instance placement by AD and fault domain after collecting complete authorized inventory; a --limit sample cannot certify spread. Include node pools, load-balancer backends, databases, storage placement, network paths and external dependencies. Two instances in different fault domains may still share a single-AD database or a single application leader.
Separate current placement from capacity to recreate it. Shape availability, reservations, quotas and subnet/service locality can constrain recovery. Inspect placement and dependency evidence without moving or restarting instances.
A resilience report should list asset class, observed count, failure boundary, shared dependency and evidence completeness. Do not label a workload highly available solely because it has multiple instances. Live evidence here establishes that three AD names were discoverable, not workload resilience.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| ExternalServerIncorrectState | A customer-owned server (DB agent, on-prem host, Exadata) is unreachable/misbehaving | id 19 [unverified] |
| IncorrectState | Resource is mid-transition (`PROVISIONING`, `TERMINATING`, `UPDATING`) | id 18 [unverified] |
