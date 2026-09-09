# Security Zones — the preventive control

Verified 2026-09-09 against OCI CLI 3.91.0. Security Zones are part of Cloud Guard and are
absent from free-tier tenancies.

## What they are
A security zone is a **compartment plus a recipe** of security-zone policies. On every
create/update OCI validates the operation against the whole recipe and **any violation denies
the operation** — at API time, for the zone's compartment *and every subcompartment in it*.
That makes it the strongest single control this skill can recommend, and a frequent cause of
mysterious 409 / `NotAuthorizedOrNotFound` on someone else's create call.

Oracle ships a predefined **Maximum Security Recipe**; it is Oracle-managed and **not
modifiable**. Build a custom recipe instead of asking to edit it.

## The CLI trap
`oci cloud-guard security-zone` exposes `create/get/update/delete/add/remove/change-compartment`
and `security-recipe` exposes `create/get/update/delete/change-compartment`. **Neither has a
`list`** — `oci cloud-guard security-zone list` fails with `No such command 'list'` `[verified]`.
Enumerate by OCID, or through Search / the Console.

```bash
oci cloud-guard security-zone get --security-zone-id "$SECURITY_ZONE_ID" --query 'data.{n:"display-name",c:"compartment-id",r:"security-zone-recipe-id",s:"lifecycle-state"}'
```
```bash
oci search resource structured-search --query-text "query SecurityZonesSecurityZone resources" --limit 50 --query 'data.items[].{n:"display-name",c:"compartment-id"}'
```
The Search type is `SecurityZonesSecurityZone` (also `SecurityZonesSecurityRecipe`,
`SecurityZonesSecurityPolicy`) `[verified live, empty here]`. A guessed name returns
`CannotParseRequest` `Unknown resource type '...'`; confirm names with
`oci search resource-type list --limit 1000`.

## Maximum Security Recipe — policy categories (verbatim identifiers, abridged)
* **Deny Public Access** — `cloud_shell_public_network`, `db_instance_public_access`,
  `public_load_balancer`, `public_buckets`, `internet_gateway`, `public_subnets`.
* **Require Encryption** (customer-managed Vault key mandatory) — `block_volume_without_vault_key`,
  `boot_volume_without_vault_key`, `file_system_without_vault_key`, `buckets_without_vault_key`.
* **Ensure Data Durability** — `database_without_backup`.
* **Restrict Resource Movement** — 11 policies stopping a resource from leaving or entering the
  zone, e.g. `bucket_in_security_zone_move_to_compartment_not_in_security_zone`,
  `instance_not_in_security_zone_move_to_compartment_in_security_zone`.
* **Restrict Resource Association** — 15 policies stopping a zone resource from being attached
  to a non-zone one, e.g. `instance_in_security_zone_in_subnet_not_in_security_zone`.
* **Ensure Data Security** — clone/restore across the zone boundary.
* **Use Only Configurations Approved by Oracle** — ~30 policies including
  `instance_without_sanctioned_image`, `security_list_to_allow_traffic_to_restricted_port`,
  `network_security_group_with_unsecure_ingress_rule`, `manage_bastion_resource`,
  `terminate_instance`, `create_drg`, `free_database_creation`.

## Consequences to state before recommending it
No internet gateway, no public subnets, no public buckets, no public load balancers, no Cloud
Shell public network, no Always-Free database creation (`free_database_creation` is denied),
and every volume, file system and bucket must carry a Vault key. **A Free Tier tenancy cannot
meaningfully use the Maximum Security Recipe.** Database policies do not apply to Exadata
Cloud@Customer; Compute Management policies cover instance configurations and instance pools.

## How to use this in an audit
A compartment in a security zone turns several findings in the CIS table into "cannot happen":
public buckets, public subnets, volumes without a required CMK. Confirm the actual
recipe and assess existing resources; zone membership alone is not proof of compliance. Where a zone exists, say which recipe backs it; where one does not,
propose it as prevention alongside the detective findings, and name the workloads it would
break. Creating or changing a zone is a mutation and belongs to the tenancy owner, not here.

Docs: https://docs.oracle.com/en-us/iaas/security-zone/using/security-zone-policies.htm
