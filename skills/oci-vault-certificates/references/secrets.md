# Secret metadata and content
Source: research/09b §20.
vault secret list/get returns metadata; secrets secret-bundle get accesses secret content. Secret bundle base64 is encoding, not encryption. Do not fetch or decode a bundle during metadata diagnosis and never put decoded content in a command argument, log or status file.
Versions have stages such as CURRENT, PENDING, PREVIOUS and DEPRECATED. Check consumer behavior before moving a version to CURRENT: applications may cache credentials, use a pinned version, or lack permission to read the new secret.
A rotation plan must cover the backing credential system, new secret version, consumer rollout, health verification and rollback overlap. Changing a secret value alone does not rotate the database or external service password.
This helper does not read bundles or create/rotate/delete secrets. SDK, external rotation functions and service-specific credentials remain [unverified] until exercised with authorized nonsecret evidence.

Documentation refresh (2026-09-09): Oracle now documents secrets under the separate [Secret Management Service](https://docs.oracle.com/en-us/iaas/Content/secret-management/overview.htm). CLI 3.91 still uses the vault secret metadata and secrets secret-bundle retrieval groups shown here.
