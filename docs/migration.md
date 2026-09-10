# Migration Copilot

Three skills separate source inventory, target decisions and infrastructure planning:
[assess](../skills/oci-migration-assess/SKILL.md),
[map and price](../skills/oci-migration-map/SKILL.md), and
[landing-zone draft](../skills/oci-migration-landing-zone/SKILL.md).

[Run the demonstration](../demos/migration-copilot/README.md) without cloud credentials.
The synthetic source export exercises CPU/memory mapping, storage performance limits,
managed-database warnings, priced subsets and network overlap checks. The emitted tfvars
are a draft, not a deployed or certified landing zone. No source credentials were used.

Source-cloud readers ingest JSON exports, not generic shell commands. AWS support includes
compute, storage, DB, network and LB shapes; GCP/Azure adapters cover compute and disks,
with remaining services explicitly unread. A normalized inventory can carry additional
reviewed service exports. Service-category mappings are not feature equivalence guarantees.

[Recorded example](evidence/migration-sample-report.md). Public price snapshots refresh
according to [freshness rules](freshness.md); unavailable/ambiguous prices remain unknown.
