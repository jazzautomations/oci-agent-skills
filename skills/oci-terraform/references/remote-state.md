# State ownership and locking
Source: research/08c §7.
State can contain passwords, secret values and full infrastructure topology. Store it in a protected backend with encryption, version history, least-privilege access and a tested recovery path. Never include state or backend credentials in a repository.
OCI Object Storage S3 compatibility and a native OCI backend have different authentication, endpoint and locking semantics. Support varies by Terraform/OpenTofu version; do not assume DynamoDB locking works against OCI or that an object bucket alone supplies a distributed lock.
Confirm the exact backend's lock behavior in current documentation before multi-writer use. [unverified] No backend or lock acquisition was exercised here. Resource Manager's managed state/jobs are an alternative with their own concurrency and IAM rules.
State rollback does not undo remote resource changes. Preserve state generations and an infrastructure recovery plan separately.
