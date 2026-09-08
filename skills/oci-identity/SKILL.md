---
name: oci-identity
description: Inspect and plan OCI tenancy, compartment, IAM policy, principal and Identity Domain configuration, including cross-tenancy scope.
---

Read [the operator contract](../../docs/operations.md). Establish authenticated
tenancy, profile/signer, region and selected compartment. Start with `oci_regions`
and `oci_compartments` if the MCP is available; report unreadable or truncated scopes.

Verified CLI examples: `identity-compartments`, `identity-regions`, `identity-policy`
in [catalog/examples.json](../../catalog/examples.json). Check current help:

```bash
oci iam compartment list --help
oci iam region-subscription list --help
oci iam policy list --help
oci iam domain list --help
oci identity-domains users list --help
```

OCI IAM policy and Identity Domain users/groups are separate control planes.
Discover the domain URL from the selected domain; domain calls require that
endpoint. Do not assume legacy `iam user` lists every domain user.

Read existing policy attachment locations and inherited grants before changing
permissions. Explain principal → verb → resource family → compartment → condition.
Dynamic-group membership and its policies are distinct. Cross-tenancy access
requires matching relationships on the involved tenancies, not a local policy alone.

For a change, preserve unrelated statements, review the diff and use ETags where
supported. Do not replace a whole policy document with one new statement. Verify
with the intended principal and minimal operation after propagation; an admin test
does not demonstrate least privilege. Keep access bootstrap separate from routine
inventory and never print credential material.

[IAM documentation](https://docs.oracle.com/en-us/iaas/Content/Identity/home.htm)
