---
name: oci-iac
description: Author and review OCI Terraform, Resource Manager and Ansible changes, including resource adoption and state ownership.
---

Read [the operator contract](../../docs/operations.md) and
[the IaC guide](../../docs/sdk-and-devops.md). Examples `iac-stacks` and `iac-jobs`
in [the catalog](../../catalog/examples.json) inspect managed Terraform resources.

```bash
oci resource-manager stack list --help
oci resource-manager job list --help
oci resource-manager stack list-terraform-versions --help
```

Establish who owns existing resources and state before generating HCL. Resource
Discovery/import can help adopt infrastructure but does not guarantee complete
coverage or a safe no-op plan. Keep imports in a separate work directory until
reviewed; never let two states manage the same resource concurrently.

For APEX/application releases, use `oracle-apex` for schema and application delivery.
Terraform owns hosting infrastructure; do not recreate an existing Autonomous
database to deploy an application export or schema migration.

Pin the provider and lockfile. Confirm managed Terraform versions separately from
the developer's local CLI; do not assume Resource Manager runs the newest Terraform.
Use the provider schema and actual plan to verify resource attributes, defaults,
replacement behavior and dependencies.

Run formatting/validation and produce a saved plan. Inspect resource addresses,
destruction/replacement, IAM/network changes and cost effects. Apply only the exact
reviewed plan under existing task authorization, with explicit confirmation for
destructive effects. State/plan files can contain secrets and are never public
artifacts. A stale or changed plan requires another review.

For Ansible, validate check-mode support per module and use modules' desired-state
semantics rather than wrapping a non-idempotent shell loop. For Pulumi, OpenTofu or
Crossplane, verify the actual provider/release; do not infer compatibility from
similar names. Verify application health after infrastructure readiness.

[Resource Manager](https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Concepts/resourcemanager.htm),
[Resource Discovery](https://docs.oracle.com/en-us/iaas/Content/dev/terraform/resource-discovery.htm)
