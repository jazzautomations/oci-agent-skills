# Backup and replication matrix

Use this matrix to locate evidence; route service-specific commands to the owning service skill.

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
