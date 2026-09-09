Purpose: pick the right IAM condition variable, operator and resource-type for an OCI policy — per-variable operator sets, the traps that silently deny, region keys, family expansion.
Source: research/04b-iam-security-cost-freetier.md §1–14, §23 + research/data/regions.json; generated 2026-09-08; verified-on CLI 3.91.0

§1 grammar · 2 variables/operators · 3 traps · 4 region keys · 5 tag vars · 6 permissions · 7 families → members · 8 dynamic groups · 9 links

## 1. Condition grammar and value types

```
where <variable> <operator> <value>
where any { <cond>, <cond>, ... }   # OR
where all { <cond>, <cond>, ... }   # AND
```

Value types: **String** in single quotes; **Pattern** `/hr*/` prefix, `/*hr/` suffix, `/*hr*/` contains; **Policy variable** — another variable on the RHS (tag vars only).

One verb, one resource-type, one principal *type* per statement. `Allow` only — no `Deny`; absence of an `Allow` is an implicit deny. Location (`in tenancy` / `in compartment X`) is part of the statement, **not** a condition — region/AD scoping uses `request.region`/`request.ad`.

## 2. General variables and their operators

Operators are **not uniform** — most take only `=` / `!=`; timestamp variables take their own.

| Variable | Type | Operators | Note |
|---|---|---|---|
| `request.user.id` / `.name` | OCID / String | `=` `!=` | the requesting user |
| `request.user.mfaTotpVerified` | Boolean | `=` `!=` | `='true'` forces MFA on that statement |
| `request.groups.id` | list of OCIDs | `=` `!=` | groups the user is in |
| `request.permission` | String | `=` `!=` | e.g. `'VOLUME_DELETE'` — §6 |
| `request.operation` | String | `=` `!=` | e.g. `'ListUsers'` |
| `request.networkSource.name` | String | `=` `!=` | network-source object name; create it first |
| `request.utc-timestamp` | ISO 8601 String | **`before` \| `after` only** | `'2020-04-01T15:00:00Z'`, `'2020-04-01Z'` |
| `request.utc-timestamp.{month-of-year, day-of-month, day-of-week}` | String | `=` `!=` `in` | `'1'`–`'12'`, `'1'`–`'31'`, `'monday'`… |
| `request.utc-timestamp.time-of-day` | String | **`between 'hh:mm:ssZ' and 'hh:mm:ssZ'` only** | |
| `request.region` | String | `=` `!=` | **3-letter key** — §4 |
| `request.ad` | String | `=` `!=` | AD name from `oci iam availability-domain list` |
| `request.principal.compartment.tag.<ns>.<key>` | String | `=` `!=` `in` `not in` | tag on the requesting *resource*'s compartment; users sit in root |
| `request.principal.group.tag.<ns>.<key>` | String | `=` `!=` `in` `not in` | tag on the requester's groups / dynamic groups |
| `target.compartment.name` / `.id` | String / OCID | `=` `!=` | the `.id` form **cannot filter a List** |
| `target.resource.tag.<ns>.<key>` | String | `=` `!=` `in` `not in` | tag on the target resource — §5 |
| `target.resource.compartment.tag.<ns>.<key>` | String | `=` `!=` `in` `not in` | tag on the target's compartment; inherits downward |

Services add their own `target.*` — Object Storage `target.bucket.name`, `target.bucket.tag.<ns>.<key>`; IAM `target.group.name`, `target.user.name`. See the service's policy-reference page.

## 3. Traps that silently deny

1. **Matching is case-insensitive.** `target.bucket.name='BucketA'` also matches `bucketa`; tag *values* likewise. Case never separates two resources.
2. **A non-applicable variable declines the request.** No value for it in the request ⇒ condition false ⇒ denied. Classic: `… use users in tenancy where target.group.name != 'Administrators'` breaks `ListUsers`/`UpdateUser` — neither carries a group. Fix with a second *unconditioned* statement (`inspect users` for List, `use users` for Update).
3. **`target.compartment.id` cannot filter a List**, only narrow the target.
4. **Clock skew ~5 min**; all times UTC, so DST changes mean editing the policy.
5. **`inspect` is not "metadata only"** — `inspect policies` returns statement text, `inspect virtual-network-family` full security-list and route-table content.
6. **Propagation.** IAM writes go to the **home region** only: "typically within 10 seconds" in-region (`oci iam policy create --help` [verified]), "several minutes" cross-region. A 403/404 right after a write is not failure.

## 4. Region keys (IAM) vs region names (quotas)

`request.region` takes the **3-letter region key**. Quota policy — a different language — takes the **full region name**, and `request.region`/`request.ad` are its *only* conditionals.

| Region name | IAM key | Region name | IAM key |
|---|---|---|---|
| `sa-saopaulo-1` | `GRU` | `us-chicago-1` | `ORD` |
| `sa-vinhedo-1` | `VCP` | `eu-frankfurt-1` | `FRA` |
| `us-ashburn-1` | `IAD` | `uk-london-1` | `LHR` |
| `us-phoenix-1` | `PHX` | | |

Table from `04b` §23 + `research/data/regions.json` (§1–14 has the bare keys only). Keys [verified] live via `oci iam region list --query "data[].[key,name]"` — realm-scoped, so the row count differs per realm (counts in `realms-endpoints.md`). Never hand-build a key.

## 5. Tag variables (TBAC)

Four variables (§2); RHS may be String, Pattern or another tag variable, `'*'`/`/*/` matching any value. Two hard limits:

- **Cannot grant List** — the resource must already be named. Add an unconditioned `inspect`, or tag the *compartment* and use `target.resource.compartment.tag.*` instead.
- **Cannot grant create** — the resource has no tag yet; `manage instances where target.resource.tag…` gives use+delete, never create.

Namespace/key characters: `a-z A-Z 0-9 _ @ - :` only; neither can be renamed. Whoever applies tags confers access — audit tag-apply rights first.

## 6. Permissions vs operations

Permissions are the atomic units, `UPPER_SNAKE`; verbs (`inspect` < `read` < `use` < `manage`, each including the previous) are bundles, and one call may need several (`AttachVolume` = `VOLUME_WRITE` + `VOLUME_ATTACHMENT_CREATE` + `INSTANCE_ATTACH_VOLUME`).

- Allowlist `where any {request.permission='GROUP_INSPECT', …}` is the hard boundary.
- Denylist `where request.permission != 'GROUP_DELETE'` **auto-grants every permission the service adds later** — never the only guard.
- Grant with `request.permission`; `request.operation` only narrows. Strings are per resource-type — re-check per service before deployment [partially unverified].

## 7. Resource-type families → members

`<verb> <family>` is **exactly equivalent to one statement per member**, and a family silently widens: a new individual resource-type is folded into its service family automatically. Generate individual resource-types for guarded policy; use a family only when that widening is intended. `resource-type-families.json` holds `family → members`.

**IAM has no family resource-type** — only individual ones (`users`, `groups`, `policies`, `compartments`, `dynamic-groups`, `tag-namespaces`, …).

## 8. Dynamic-group matching rules

A rule over principals, not a user list: `ALL {instance.compartment.id = '<ocid>'}`, `ANY {instance.id = '<ocid>', …}`, `ALL {resource.type = 'fnfunc', resource.compartment.id = '<ocid>'}`, or `tag.<ns>.<key>.value = '<v>'` — the tag form is maintainable. Variables: `instance.id`, `instance.compartment.id`, `resource.id`, `resource.compartment.id`, `resource.type`; that value list is illustrative, per-service pages authoritative [partially unverified]. They live in the tenancy root, home region only — `oci iam dynamic-group` (= `identity-domains dynamic-resource-group` under domains).

## 9. Links (HTTP 200 on 2026-09-08)

- Conditions — https://docs.oracle.com/en-us/iaas/Content/Identity/policysyntax/conditions.htm
- Policy reference — https://docs.oracle.com/en-us/iaas/Content/Identity/Reference/policyreference.htm
- Resource-types & families — https://docs.oracle.com/en-us/iaas/Content/Identity/policyreference/corepolicyreference_topic-ResourceTypes.htm
- Tag-based access control (TBAC) — https://docs.oracle.com/en-us/iaas/Content/Tagging/Tasks/managingaccesswithtags.htm
