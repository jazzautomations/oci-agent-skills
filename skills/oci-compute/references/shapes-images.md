# Shapes and images
Source: research/04c Compute; research/06c §§1–2.
Resolve an image in the selected region, filtering by OS version and target shape, newest first. Arm images cannot boot x86 shapes. Check application compatibility separately.
Read ocpu-options and memory-options rather than copying a fixed ratio. Shape lists can repeat across ADs; retain placement before deduplicating. Fixed shapes do not take flexible shape configuration.
A listed shape does not imply available limits or hosts. capacity_probe.sh reports limits only; physical capacity is unknown. The create-capacity-report operation is excluded by the wrapper.
The research contains conflicting A1 free allowances. Route current entitlements to oci-free-tier. [unverified] PAYG priority folklore is not a capacity guarantee.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| InvalidParameter | Flex shape config outside the allowed ratio (e.g. A1 requires 6 GB per OCPU) | id 41 [unverified] |
| RelatedResourceNotAuthorizedOrNotFound | The subnet/image OCID in the body is cross-region, deleted, or unreadable | id 39 [unverified] |
