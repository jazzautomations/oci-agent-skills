# Backups, clones and volume groups
Source: research/04c Block; research/09b §28.
A backup policy must be assigned to the volume/boot volume to protect it. Read the asset assignment rather than inferring protection from the existence of a policy. Record retention and destination-region behavior from the policy itself; do not hardcode historical Bronze/Silver/Gold schedules.
Backups and group backups are crash-consistent unless applications are quiesced. A successful backup status is not a restore test. Clones are local operational copies, not automatically independent disaster recovery.
Cross-region copies require destination permissions and compatible key access. Keep recovery-point time, source lineage and encryption-key lifetime together. Reassigning a policy replaces the prior assignment; preserve its ID for a rollback proposal.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| `(?i).*volume.*already attached.*` / `Conflict` | Boot volume still attached to a terminated-but-not-deleted instance | id 42 [unverified] |
| ResourceLocked | A resource lock (full/delete) or a parent-tenancy quota lock | id 21 [unverified] |
