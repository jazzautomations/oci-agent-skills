# Migration assessment

SYNTHETIC fixture; no source account read.
USD list price, pre-discount; snapshot 2026-09-09T16:34:38.537Z; 730 hours/month.
Priced subset: 6/15 resources, USD 539.77/month. Full-estate saving: unknown.

| Kind | Resource | OCI target | Source scenario USD/month | OCI subset USD/month |
|---|---|---|---:|---:|
| compute | sha256:308f197f7f30 | VM.Standard.E5.Flex | 70.08 | 33.58 |
| compute | sha256:32a3d871ca90 | VM.Standard.E5.Flex | 70.08 | 33.58 |
| compute | sha256:00e66ffd5d5d | VM.Standard.E5.Flex | unknown | 134.32 |
| compute | sha256:c69817f08fc6 | VM.Standard.E5.Flex | 367.92 | 181.04 |
| block | sha256:b506a759f03e | needs input | unknown | unknown |
| block | sha256:5e3ae5034724 | needs input | unknown | unknown |
| block | sha256:c71fd9c1033d | Block volume 20 VPU | unknown | 29.75 |
| block | sha256:1a6294844cb7 | Block volume 60 VPU | unknown | 127.5 |
| block | sha256:eabf3a4f77be | needs input | unknown | unknown |
| object | sha256:a1687374285e | Object Storage | unknown | unknown |
| database | sha256:7f8f071b50c3 | OCI Database with PostgreSQL | unknown | unknown |
| database | sha256:a67e9602ffc3 | Base Database; Autonomous requires suitability assessment | unknown | unknown |
| network | sha256:446d617868c1 | VCN + DRG | unknown | unknown |
| lb | sha256:b43a19998d2c | Flexible Load Balancer | unknown | unknown |
| dns | sha256:7672b27af370 | OCI DNS | unknown | unknown |

Comparable subset: 3 resources; source USD 508.08, OCI USD 248.2. These are 730-hour capacity scenarios, not current bills.

## Coverage and price provenance

Regions scanned: us-east-1
Services not readable: eks (AccessDenied: eks:ListClusters), k8s not exported, serverless not exported
OCI retrieval: 2026-09-10T09:25:58.590661+00:00
- [Linux on-demand](https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/US%20East%20%28N.%20Virginia%29/Linux/index.json); snapshot 2026-09-09T16:49:38Z.

## Assessment questions

- Commercial vehicle: PAYG or Universal Credits? needs customer input
- Windows, Marketplace, encrypted, >400 GB boot or multi-disk assets? needs customer input
- Which sources fit OCM and which require rebuild? OCM candidate; precheck required
- Which workloads need an Arm rebuild? 0 Arm candidates; rebuild validation required
- Largest security rule and group counts? needs customer input
- Peak concurrent connections and required network capacity? needs customer input
- IAM statement counts and compartment design? needs customer input
- Database engine, edition, version and migration precheck? oracle-ee; postgres; editions and migration prechecks need customer input
- IPv4/dual-stack subnet requirements? needs customer input
- Who pays one-time source egress and migration overlap? needs customer input

## Exclusions and decisions

- Committed discounts and source contracts
- Source egress and overlap during migration
- Database/license/storage extras
- Network, object requests, load balancer bandwidth, backups, support, HA and operational labor
- GCP live price requires a customer API key/export; absent here
- Free Tier is not a production capacity or retention guarantee
- Multi-AZ topology cannot be replaced by fault domains without an HA review
- Off-cloud backups, tested restore, support escalation and a reversible cutover plan are required
- Confirm regional capacity and quotas before promising deployment

## Resource warnings

- sha256:308f197f7f30: Shape capacity, performance, connection limits and HA must be validated; 730 hours assumed
- sha256:32a3d871ca90: Shape capacity, performance, connection limits and HA must be validated; 730 hours assumed
- sha256:00e66ffd5d5d: Commercial Linux subscription and portability unresolved; license uplift excluded
- sha256:00e66ffd5d5d: Shape capacity, performance, connection limits and HA must be validated; 730 hours assumed
- sha256:c69817f08fc6: Stopped source: 730-hour capacity scenario, not an estimate of its current bill
- sha256:c69817f08fc6: Shape capacity, performance, connection limits and HA must be validated; 730 hours assumed
- sha256:b506a759f03e: IOPS/throughput exceeds supported VPU envelope; do not clamp
- sha256:5e3ae5034724: IOPS/throughput exceeds supported VPU envelope; do not clamp
- sha256:1a6294844cb7: UHP requires multipath and supported compute shape
- sha256:eabf3a4f77be: IOPS/throughput unknown; no unconditional gp3 mapping
- sha256:a1687374285e: Usage, feature parity and shared tenancy allowances unresolved; no price invented
- sha256:7f8f071b50c3: Engine/version/edition, extension parity, HA, downtime and licensing need migration prechecks; database price excluded
- sha256:a67e9602ffc3: Engine/version/edition, extension parity, HA, downtime and licensing need migration prechecks; database price excluded
- sha256:446d617868c1: Usage, feature parity and shared tenancy allowances unresolved; no price invented
- sha256:b43a19998d2c: Usage, feature parity and shared tenancy allowances unresolved; no price invented
- sha256:7672b27af370: Usage, feature parity and shared tenancy allowances unresolved; no price invented
