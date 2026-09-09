# CDB/PDB, backup, patch and Data Guard

Record CDB, PDB, database home, engine version, open mode and topology before diagnosis. SGA is shared instance memory; PGA is process memory. Do not infer a storage shortage from memory pressure. Distinguish permanent, undo and temporary tablespaces and ASM capacity before proposing growth.

The clone generations use different flags: local-clone/remote-clone take pluggable-database-id; create-local-clone/create-remote-clone use source-pdb-id and cdb-id. Do not mix them. Listener operations use lsnrctl on a customer-managed host; no listener CLI API exists. SPFILE changes can take effect only at next restart.

Read db backup metadata and the automatic backup configuration separately. RMAN is a host/database tool, not a CLI subcommand and not exposed on ADB. A restore is in-place and needs exactly one recovery selector: latest, timestamp or database-scn; syntax alone cannot prove recovery. Retain a tested recovery target and logs before a DBA-approved restore.

Patch enumeration uses db patch list by-database / by-db-system or list-db-home / list-vm-cluster. PRECHECK, patch, upgrade and rollback still create service work; none runs here. RAC rolling eligibility depends on the exact patch and services. Route estate orchestration to oci-migration-patching.

Data Guard association list/get uses both database and association identity. Planned switchover preserves a synchronized pair; emergency failover can lose data and needs reinstate/rebuild. Do not present either as an automatic fix. Document lag, fencing, app connection changes and rollback feasibility.
