Purpose: write a syntactically valid OCI IAM policy statement and know what it really grants.
Source: research/04b-iam-security-cost-freetier.md §1-10; verified-on OCI CLI 3.91.0, 2026-09-09.

## Contents
1 grammar · 2 subjects · 3 verbs · 4 resource-types and families · 5 location and paths · 6 conditions · 7 Endorse/Admit/Define · 8 home region and propagation · 9 links

## 1. Grammar

```
Allow <subject> to <verb> <resource-type> in <location>
Allow <subject> to <verb> <resource-type> in <location> where <conditions>
```

`Allow` is the only start word for same-tenancy policy. **There is no `Deny`** — absence of an
Allow is the deny. One verb, one resource-type, one principal *type* per statement; several
principals of that type may be comma-separated. Extra spaces and line breaks are ignored.
Location is written explicitly even where the identity-domains overview calls it optional.

## 2. Subjects

```
group '<domain>'/'<group>' | group id <group_ocid>
| dynamic-group '<domain>'/'<dg>' | dynamic-group id <dg_ocid>
| any-group | any-user | service '<service_name>'
```

The `<domain>/` prefix is **required** for a non-default identity domain and may be omitted for
`Default`. Prefer `group id <ocid>` in generated policy: immune to renames. `any-group` covers
every group *and* dynamic group; `any-user` additionally covers resource, instance and service
principals, and Oracle recommends against it — narrow with `any-group` or a principal-type
condition instead.

## 3. Verbs

`inspect` < `read` < `use` < `manage`; each includes the one before it.

- `inspect` = List without confidential or user-specified metadata. **Not "metadata only":**
  `inspect policies` returns the statement text, and `inspect virtual-network-family` returns
  complete security lists and route tables.
- `read` = `inspect` + Get, including user-specified metadata.
- `use` = `read` + update existing resources, **except** where update is effectively create
  (`UpdatePolicy`, `UpdateSecurityList`) — those need `manage`.
- `manage` = every permission, create and delete included.

The exact meaning is per resource-type; confirm on the service's page under
`/Content/Identity/policyreference/`.

## 4. Resource-types and families

Three forms: individual (`vcns`, `buckets`, `policies`), family aggregate (`instance-family`),
or `all-resources`. `<verb> <family>` is exactly equivalent to one statement per member, and a
family **silently widens**: a new individual type is folded into its service family
automatically. Generated policy should name individual types. Member lists and the caveats live
in the shared `resource-type-families.json`. **IAM itself has no family** — only `users`,
`groups`, `policies`, `compartments`, `dynamic-groups`, `tag-namespaces` and friends.

Some operations need several resource-types at once (`LaunchInstance` = instances + network);
permissions are additive across the groups a principal belongs to.

## 5. Location and compartment paths

```
in tenancy | in compartment <name> | in compartment id <compartment_ocid>
```

There is no region or AD element — scope those with the `request.region` / `request.ad`
conditions. A policy on compartment A also applies to its descendants. A policy is attached to
exactly one compartment at creation and **attachment cannot be changed afterwards**; where it is
attached decides who may edit or delete it. When the target is neither the attachment
compartment nor its direct child, write the colon path: attached to A, targeting C under B, is
`in compartment CompartmentB:CompartmentC`; attached to the tenancy it is
`CompartmentA:CompartmentB:CompartmentC`.

## 6. Conditions

```
where <variable> <operator> <value>
where any { <cond>, ... }   # OR
where all { <cond>, ... }   # AND
```

Values are Strings in single quotes or Patterns `/hr*/`, `/*hr/`, `/*hr*/`. Per-variable
operator sets, the tag variables and the traps that silently deny are in the shared
`iam-variables.md`; read it before writing a `where` clause. The two that cost the most time:
matching is **case-insensitive**, and a variable the request carries no value for makes the
condition false, so the request is **denied**.

Prefer the allowlist form `where any { request.permission='X', ... }` over the denylist
`where request.permission != 'Y'` — the denylist auto-grants every permission the service adds
later.

## 7. Endorse / Admit / Define (cross-tenancy)

`Endorse` lives in the **source** tenancy, `Admit` in the **destination**, and `Define` aliases a
tenancy or group OCID inside the *same policy* as the statement that uses it. Either half alone
grants nothing — both tenancies must agree, and both must be subscribed to the same regions.

```
# source tenancy
Define tenancy DestinationTenancy as ocid1.tenancy.oc1..<redacted>
Endorse group StorageAdmins to manage object-family in tenancy DestinationTenancy
# destination tenancy
Define tenancy SourceTenancy as ocid1.tenancy.oc1..<redacted>
Define group StorageAdmins as ocid1.group.oc1..<redacted>
Admit group StorageAdmins of tenancy SourceTenancy to manage object-family in compartment SharedBuckets
```

Generate the narrowed pair above, not `in any-tenancy`.

## 8. Home region and propagation

Users, groups, policies, compartments, dynamic groups and federation resources are created and
changed **only in the tenancy's home region**, which cannot be changed after provisioning. Send
IAM writes to the home-region endpoint; a write to another region returns `NotAllowed` 403 with
`must be directed at the home region`. New policies "take effect typically within 10 seconds"
in-region (`oci iam policy create --help` [verified]) and take **several minutes** to reach every
subscribed region — a 403 or 404 immediately after a write is not proof the write failed.

Every policy from the home region is enforced in a newly subscribed region by default; restrict
with `where request.region = '<3-letter key>'`.

## 9. Links

- Policy syntax: https://docs.oracle.com/en-us/iaas/Content/Identity/policysyntax/policy-syntax.htm
- Verbs and resource-types: https://docs.oracle.com/en-us/iaas/Content/Identity/Reference/policyreference.htm
- Cross-tenancy: https://docs.oracle.com/en-us/iaas/Content/Identity/policieshow/iam-cross-domain.htm
- Managing regions: https://docs.oracle.com/en-us/iaas/Content/Identity/regions/managingregions.htm
