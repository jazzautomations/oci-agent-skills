# Replication and sync
Source: research/04c Object Storage; research/09b §29.
Replication requires compatible bucket settings, service-principal permissions and an explicitly selected destination region. Inspect source/destination policy and failover semantics before presenting creation or make-bucket-writable; failover is not an ordinary reversible update.
Sync with delete can remove destination-only objects. Establish direction, local root, prefix and exclusions first; a dry-run preview is not execution authorization. Avoid turning metadata inspection into an upload or deletion.
Uncommitted multipart parts are billable and absent from object list. multipart_audit.sh lists one bounded page only; an empty sample does not prove all uploads are gone. Aborting an upload destroys its ability to resume; inventory first, then propose only selected upload IDs.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| KmsKeyDisabled | Bucket's customer-managed key was disabled/deleted, or the Object Storage service principal lost `use keys` | id 79 [unverified] |
| BucketNotFound | Wrong bucket name, wrong namespace, or wrong region | id 72 [verified] |
