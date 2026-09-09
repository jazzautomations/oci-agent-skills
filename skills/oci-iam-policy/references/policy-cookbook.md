Purpose: ready-to-adapt least-privilege statement sets, TBAC recipes and the separate quota language.
Source: research/04b-iam-security-cost-freetier.md §6b, §11, §13; verified-on OCI CLI 3.91.0, 2026-09-09.

## Contents
1 read-only agent group · 2 scoped operator group · 3 tag-based access (TBAC) · 4 dynamic-group rules · 5 quota policy language · 6 links

## 1. Read-only agent group

Attach at the tenancy. Goal: enumerate and describe everything, read no secret material, read no
policy text, mutate nothing.

```
Allow group AI-Agent-Readers to inspect all-resources in tenancy
Allow group AI-Agent-Readers to read all-resources in tenancy where all {
  request.permission != 'SECRET_BUNDLE_READ',
  request.permission != 'SECRET_READ',
  request.permission != 'KEY_READ',
  request.permission != 'POLICY_READ',
  request.permission != 'AUTH_TOKEN_INSPECT',
  request.permission != 'CUSTOMER_SECRET_KEY_INSPECT' }
```

Tell the user, every time, before this ships:

- Do **not** add `inspect policies` unless disclosing policy text is acceptable — `ListPolicies`
  returns the statements themselves.
- `inspect virtual-network-family` already returns full security-list and route-table content.
  There is no names-only mode for Networking.
- Never grant `read secret-bundles`; that is the plaintext secret. `read secret-family` without
  the bundle permission stays metadata-only.
- The `!=` list is a denylist and auto-grants future permissions. For a hard boundary replace it
  with `any { request.permission='X', ... }` enumerated from the per-service reference tables.
- Where the agent runs on OCI, prefer an instance or resource principal plus a dynamic group over
  a static user with a long-lived API key.

Narrower variants:

```
Allow group AI-Agent-Readers to inspect all-resources in compartment Agent-Sandbox
Allow group AI-Agent-Readers to read all-resources in compartment Agent-Sandbox where request.permission != 'SECRET_BUNDLE_READ'
Allow dynamic-group AI-Agent-Instances to read all-resources in compartment Agent-Sandbox
```

Optional hard guards, added as their own statements:

```
Allow group AI-Agent-Readers to inspect all-resources in tenancy where request.user.mfaTotpVerified='true'
Allow group AI-Agent-Readers to inspect all-resources in tenancy where all {
  request.utc-timestamp.day-of-week in ('monday','tuesday','wednesday','thursday','friday'),
  request.region = 'GRU' }
```

## 2. Scoped operator group

One compartment; operate compute and storage, never delete; no IAM or networking changes; MFA and
corporate network required. Attach at the parent of `Project-A`.

```
Allow group Ops-Compartment-Operators to inspect all-resources       in compartment Project-A
Allow group Ops-Compartment-Operators to read virtual-network-family in compartment Project-A
Allow group Ops-Compartment-Operators to use instance-family in compartment Project-A where all {
  request.user.mfaTotpVerified = 'true',
  request.networkSource.name   = 'corpnet',
  request.utc-timestamp.day-of-week in ('monday','tuesday','wednesday','thursday','friday'),
  request.permission != 'INSTANCE_DELETE' }
Allow group Ops-Compartment-Operators to manage volumes in compartment Project-A where
  any { request.permission='VOLUME_CREATE', request.permission='VOLUME_UPDATE',
        request.permission='VOLUME_WRITE',  request.permission='VOLUME_INSPECT' }
Allow group Ops-Compartment-Operators to manage objects in compartment Project-A where all {
  target.bucket.name = 'project-a-artifacts', request.permission != 'OBJECT_DELETE' }
Allow group Ops-Compartment-Operators to use instance-family in compartment Project-A
  where request.utc-timestamp before '2027-01-01T00:00Z'
```

Bucket names match case-insensitively, so `project-a-artifacts` and `Project-A-Artifacts` are the
same target. The permission identifier strings above follow the Core Services naming convention
and are `[partially unverified]` — re-check each one against its service's "Permissions Required
for Each API Operation" table before deployment.

## 3. Tag-based access control

Requestor side: `request.principal.group.tag.<ns>.<key>`,
`request.principal.compartment.tag.<ns>.<key>` (users live in the root compartment, so for user
principals the tag must be on the tenancy). Target side: `target.resource.tag.<ns>.<key>`,
`target.resource.compartment.tag.<ns>.<key>`. Operators `=`, `!=`, `in ( )`, `not in ( )`; the
right side may be a String, a Pattern, or another policy variable.

```
allow group GroupA to use all-resources in compartment HR where target.resource.tag.HR.Project = '*'
allow group GroupA to manage all-resources in tenancy where target.resource.compartment.tag.Operations.Project = 'Prod'
allow dynamic-group InstancesA to manage instances in tenancy where request.principal.compartment.tag.Operations.Project = 'Prod'
```

Two limits that break TBAC designs:

1. `target.resource.tag.*` **cannot grant List** — add a separate unconditioned `inspect`
   statement, or tag the compartment instead.
2. `target.resource.tag.*` **cannot grant create** — the resource has no tag yet, so
   `manage instances where target.resource.tag...` yields use and delete but not create.

Namespaces and keys used in policy accept only `a-z A-Z 0-9 _ @ - :` and cannot be renamed. Tag
values are case-insensitive. Whoever can apply a tag can confer access: audit tag-apply
permissions before adopting TBAC.

## 4. Dynamic-group matching rules

```
ALL {instance.compartment.id = 'ocid1.compartment.oc1..<redacted>'}
ANY {instance.id = 'ocid1.instance.oc1..<redacted>', instance.id = 'ocid1.instance.oc1..<redacted>'}
ALL {resource.type = 'fnfunc', resource.compartment.id = 'ocid1.compartment.oc1..<redacted>'}
ANY {instance.compartment.id = 'ocid1...<redacted>', tag.<namespace>.<key>.value = '<value>'}
```

Variables: `instance.id`, `instance.compartment.id`, `resource.id`, `resource.compartment.id`,
`resource.type`, and defined-tag matching. The `resource.type` value list (`fnfunc`,
`dataflowapplication`, `autonomousdatabase`, `datasciencenotebooksession`, `odapp`) is
`[partially unverified]` — the per-service pages are authoritative. Tag-based rules are the
maintainable form: a new instance joins by being tagged. Dynamic groups live in the tenancy root
and are created in the home region only.

## 5. Quota policy — a different language

Quotas are set by administrators, not Oracle, and do not use IAM grammar.

```
zero  compute-core quotas in tenancy
set   compute-core quota standard-e4-core-count to 240 in compartment MyCompartment where request.region = us-phoenix-1
unset compute-core quota standard2-core-count in compartment productionApp
set   database quota /*exadata*/ to 1 in tenancy
```

`set` / `unset` / `zero` + service family + `quota`/`quotas` + quota name (wildcards allowed) +
`to <value>` + `in tenancy | in compartment <path>` + optionally `where request.region` or
`where request.ad` — those two are the **only** conditionals, and they take the **full region
name**, not the 3-letter IAM key. AD-scoped quotas are per AD. Subcompartment usage counts toward
the parent. Within one policy a later statement supersedes an earlier one on the same resource;
across policies the most restrictive wins, and the compartment the policy lives in does not
affect precedence. Oracle service limits always outrank a quota.

## 6. Links

- Access control with tags: https://docs.oracle.com/en-us/iaas/Content/Tagging/Tasks/managingaccesswithtags.htm
- Dynamic groups: https://docs.oracle.com/en-us/iaas/Content/Identity/dynamicgroups/managingdynamicgroups.htm
- Quota policy syntax: https://docs.oracle.com/en-us/iaas/Content/Quotas/Concepts/quota_policy_syntax.htm
