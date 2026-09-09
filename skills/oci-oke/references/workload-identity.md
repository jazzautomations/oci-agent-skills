# Workload identity
Source: research/09a §18.
Workload identity is scoped by cluster, namespace and service account, and requires an enhanced cluster. It is distinct from node instance principals and from image-pull credentials. Dynamic groups are not the workload identity mechanism.
[unverified] Research's exact workload IAM condition strings and workload-mapping setup were not exercised. Use the shared IAM reference and current policy documentation before presenting a policy; do not copy manage-all-resources grants.
For OCIR pulls, verify registry namespace, identity-domain username, image digest, namespace-local pull secret and node egress. An OCI auth token is different from an API signing key or Console password. Do not print either.
