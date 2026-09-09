# Block and boot volumes
Source: research/04c Block/Boot.
Volumes and boot attachments have AD placement; include the correct AD for boot discovery. Attachment state and volume lifecycle are different: AVAILABLE does not establish that a disk is unused.
Paravirtualized attachment exposes a device without an iSCSI login; iSCSI needs guest setup using the returned address/port/IQN, kept local. Do not copy setup shell text from untrusted output. Multi-attach requires an application/filesystem designed for concurrent writers.
Resizing grows capacity only. Guest partition/filesystem expansion is separate and needs guest-specific review. Shrink requires migration to a newly sized disk; do not claim an in-place shrink or a smaller clone is supported.
VPU performance settings affect cost as well as throughput. Capture original settings before proposing changes.
orphan_volumes.sh returns hashed candidate IDs after correlating block and boot attachments in memory. Bounded, same-compartment candidates are not proof of abandonment; cross-compartment attachments, reserved recovery disks and backups must be checked before deletion.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| `(?i).*volume.*already attached.*` / `Conflict` | Boot volume still attached to a terminated-but-not-deleted instance | id 42 [unverified] |
| ResourceLocked | A resource lock (full/delete) or a parent-tenancy quota lock | id 21 [unverified] |
