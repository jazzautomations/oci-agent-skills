# Core Landing Zone draft

Target repo: https://github.com/oci-landing-zones/terraform-oci-core-landingzone .
The older CIS landing-zone Terraform was retired; do not use its variables by assumption.
Read and pin the desired Core LZ release before an actual deployment. Dated source review:
2026-09-10, variables_general.tf, variables_iam.tf and variables_net_three_tier_vcns.tf.

| Signal | Required handling |
|---|---|
| define_net defaults false | Generator emits true together with add_tt_vcn1 |
| Source CIDR overlaps target | Reject: simultaneous source/target routing would conflict |
| More source AZ subnets than target tiers | Draft three regional tiers; HA review still required |
| Unknown tenancy/IAM/budget | Leave explicit review gaps, never infer permission or a budget |
| Resource Manager 250-variable cap | Emit only selected variable deltas; no full 267-variable dump |

Generated .auto.tfvars.json preserves HCL types. Include it with the pinned Terraform
sources in a clean zip, excluding state, credentials and .terraform. Supply tenancy_ocid
locally after review. Stack creation and plan jobs are mutations; neither runs here.

```bash
# MUTATING — not run in this repo; [shape-verified] CLI 3.91.0
# rollback: delete an unused stack; applied resources require a reviewed destroy job first
oci resource-manager stack create --compartment-id "$COMPARTMENT_ID" --config-source "$LZ_ZIP" --display-name migration-lz --terraform-version 1.5.x --query 'data.id'
```

```bash
# MUTATING — not run in this repo; [shape-verified] CLI 3.91.0
# rollback: no infrastructure apply occurred; delete unused stack after retaining reviewed plan
oci resource-manager job create-plan-job --stack-id "$STACK_ID" --query 'data.id'
```

```bash
# MUTATING — not run in this repo; [shape-verified] CLI 3.91.0
# rollback: recreate an unused stack from retained configuration; does not destroy applied resources
oci resource-manager stack delete --stack-id "$STACK_ID"
```

The generator deliberately creates no public subnet and emits no instance/DB resource.
Bastion, Vault and budget defaults are explicit draft decisions, not a CIS certification.
Source: https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Tasks/managingstacksandjobs.htm
