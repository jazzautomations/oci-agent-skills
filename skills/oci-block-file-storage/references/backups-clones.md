# Backups, clones and volume groups
Source: research/04c Block; research/09b §28.
A backup policy must be assigned to the volume/boot volume to protect it. Read the asset assignment rather than inferring protection from the existence of a policy. Record retention and destination-region behavior from the policy itself; do not hardcode historical Bronze/Silver/Gold schedules.
Backups and group backups are crash-consistent unless applications are quiesced. A successful backup status is not a restore test. Clones are local operational copies, not automatically independent disaster recovery.
Cross-region copies require destination permissions and compatible key access. Keep recovery-point time, source lineage and encryption-key lifetime together. Reassigning a policy replaces the prior assignment; preserve its ID for a rollback proposal.
