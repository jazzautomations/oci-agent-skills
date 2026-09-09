# Replication and sync
Source: research/04c Object Storage; research/09b §29.
Replication requires compatible bucket settings, service-principal permissions and an explicitly selected destination region. Inspect source/destination policy and failover semantics before presenting creation or make-bucket-writable; failover is not an ordinary reversible update.
Sync with delete can remove destination-only objects. Establish direction, local root, prefix and exclusions first; a dry-run preview is not execution authorization. Avoid turning metadata inspection into an upload or deletion.
Uncommitted multipart parts are billable and absent from object list. multipart_audit.sh lists one bounded page only; an empty sample does not prove all uploads are gone. Aborting an upload destroys its ability to resume; inventory first, then propose only selected upload IDs.
