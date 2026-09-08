---
name: oci-reliability
description: Plan and operate OCI disaster recovery, migrations and fleet maintenance using dependency, downtime and recovery evidence.
---

Read [the operator contract](../../docs/operations.md). Catalog examples
`reliability-dr`, `reliability-migrations` and `reliability-os` inspect configuration.

```bash
oci disaster-recovery dr-protection-group list --help
oci database-migration migration list --help
oci cloud-migrations migration list --help
oci os-management-hub managed-instance list --help
```

For continuity, start with workload dependencies, RPO/RTO, source/target regions,
data replication, DNS/traffic switch and identity/network prerequisites. Distinguish
backup, replication, recovery plan and a completed restore drill. Configuration
alone does not demonstrate recovery time or data integrity.

For Full Stack DR, review plan steps and supported prechecks before a drill or
switchover. These operations can disrupt production and have no universal dry-run.
Confirm exact affected resources and recovery direction before destructive actions.
Preserve the timeline and validate application/data health in the target region.

For migration, separate Cloud Migrations (infrastructure), Database Migration/ZDM
(database) and application replatforming. Validate engine/version, connectivity,
replication lag, cutover window and rollback boundary. Do not equate an exported
Terraform configuration with a data migration.

For OS Management Hub, Ksplice or fleet patching, identify managed instance groups,
software sources, maintenance windows, reboot requirements and rollout batches.
Verify on a representative non-production target before broad rollout. Maintenance
completion must include application health and exceptions, not just package status.

[Full Stack DR](https://docs.oracle.com/en-us/iaas/disaster-recovery/index.html),
[OS Management Hub](https://docs.oracle.com/en-us/iaas/os-management-hub/index.html)
