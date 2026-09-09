# File Storage
Source: research/04c FSS; research/09b §30.
File systems, mount targets, export sets and exports are separate objects. Diagnose mount target placement/IP, export path, client CIDR options, network ports and guest NFS mount configuration in that order.
Set explicit export options, source CIDRs and root squash appropriate to the client. Do not infer permissive defaults from an empty export-options array. Updating options replaces the array; preserve ordering and complete previous options.
Snapshots appear under .snapshot and consume storage. They are not an independent regional backup; a file-system loss can destroy recovery access. Snapshot policy, replication and a tested recovery procedure address different requirements.
Do not run guest mount, growfs, filesystem repairs, attachment or snapshot deletion during read-only diagnosis.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| `(?i).*volume.*already attached.*` / `Conflict` | Boot volume still attached to a terminated-but-not-deleted instance | id 42 [unverified] |
| ResourceLocked | A resource lock (full/delete) or a parent-tenancy quota lock | id 21 [unverified] |
