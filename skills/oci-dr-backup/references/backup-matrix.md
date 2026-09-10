# Backup and replication matrix

Use this matrix to locate evidence; route service-specific commands to the owning service skill.

For a policy-removal question, distinguish the scheduling policy, its assignment
to the asset, and already-created backups. Inspect each backup's expiration and
any independent copies before describing retained recovery coverage. Oracle's
[Block Volume backup policy documentation](https://docs.oracle.com/en-us/iaas/Content/Block/Tasks/schedulingvolumebackups.htm)
states that policy-based backups eventually expire; stopping a schedule does not
justify promising indefinite retention. Manual backups are a separate retention
case. Do not infer the exact effect of an assignment change from the word
"delete": confirm the operation in the service reference and preserve evidence
before delegating a scoped proposal. No removal is executed by this assessment.

| Asset | Evidence | Recovery constraint |
|---|---|---|
| Block and boot volumes | Backup policy assignment, completed backup, destination copy | Crash consistency does not prove application consistency; a missing assignment does not rule out manual backups |
| Volume groups | Group membership and group backup completion | Coordinate related volumes and application quiescence |
| Oracle databases | Backup/recovery policy, logs, recovery-point coverage | Engine/version, keys, credentials and consistency; replication is not a historical backup |
| Object Storage | Versioning, lifecycle, retention and replication policies | Replication can propagate unwanted changes; evaluate overwrite/delete behavior and independent recovery copies |
| File Storage | Snapshot policy, snapshot state and replication | Same-filesystem snapshots share failure boundaries; recovery copy writes files |
| Managed data services | Service-specific backup and restore compatibility | Region/engine/version and application endpoints must be supported |

Inventory both regions explicitly. A policy object without an asset assignment protects nothing by itself; an assignment without recent successful backups does not prove recoverability. Preserve time zone, retention, recovery-point coverage, encryption-key lifecycle and any copy lag.
Do not delete old backups or weaken immutable retention to save cost during triage. Cross-region copying, enabling replication, archive restore and making a destination writable are mutations. A restore drill should use an isolated target and validate data plus application behavior before recording achieved RPO/RTO.
