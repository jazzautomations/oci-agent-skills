Purpose: the fifteen OCI CLI failure modes that look like something else, each with the signal an agent can key on.
Source: research/04a-cli-auth-ergonomics.md §3 (P1–P15), §2.9–2.10; generated 2026-09-09; verified-on CLI 3.91.0, live tenancy `oc1`/`us-chicago-1`.

## Contents
1. Scope and identity — P1–P5
2. Output and completeness — P6–P8
3. Capacity and limits — P9–P11
4. Timing, naming and guard evasion — P12–P15

## 1. Scope and identity

**P1 — IAM writes live in the home region.** Identity writes (users, groups, policies,
compartments, tags) must target the home region; other regions serve reads with
replication lag. One call names it [verified live 2026-09-09 → `us-chicago-1`]:
`oci iam region-subscription list --tenancy-id "$T" --all --query 'data[?"is-home-region"]."region-name"'`

**P2 — Region subscription looks like bad credentials.** An unsubscribed region answers
`401 NotAuthenticated` — "The required information to complete authentication was not
provided or was incorrect." [verified live 2026-09-09: `oci iam user list --region
us-phoenix-1` on a tenancy subscribed only to `us-chicago-1`]. On any 401, check the
subscription list *before* touching the key or fingerprint.

**P3 — `NotAuthorizedOrNotFound` is deliberately ambiguous.** A made-up compartment OCID
returns `404 NotAuthorizedOrNotFound: "Authorization failed or requested resource not
found."` [verified live 2026-09-09]. It covers a wrong OCID, a right OCID in another
region, a missing policy, and a genuinely deleted resource. Never report "does not exist".

**P4 — Tenancy OCID is not interchangeable with compartment OCID.** The tenancy *is* the
root compartment, so `ocid1.tenancy.oc1..` is legal for `--compartment-id` — but
`--tenant-id` (Search, `usage-api`) rejects a compartment OCID. Omit `--compartment-id`
and the CLI silently substitutes the profile's `tenancy` [verified], widening scope.

**P5 — Root versus child compartment.** `--compartment-id-in-subtree true` is legal only
on the tenancy root; passing a child id is an error, not a silent narrowing [verified].
Without the flag a listing returns first-level children only — never grandchildren — so
nested resources look absent. `--access-level ACCESSIBLE` additionally returns a
*restricted set of fields* for indirect grants: a missing field can be an access-level
artefact, not missing data.

## 2. Output and completeness

**P6 — Truncated lists are the number-one correctness bug.** See
`pagination-waiters.md`; the warning goes to stderr and stdout-only readers miss it.

**P7 — Three key vocabularies.** CLI response keys are kebab-case (`"lifecycle-state"`,
`"display-name"`); Search `--query-text`, `--from-json` and `--generate-*-json-input` are
camelCase (`lifeCycleState`, `displayName`, `compartmentId`); `--skip-deserialization`
flips output back to camelCase and breaks queries written for the normal path [all
verified]. Hyphenated keys must be double-quoted in JMESPath — unquoted
`data[?lifecycle-state=='ACTIVE']` parses as subtraction and returns null.

A second nesting trap [verified live 2026-09-09]: in `oci audit event list`, `event-time`
is a top-level key but `event-name` and `identity."principal-name"` live *inside* each
item's `data` object. `--query 'data[].{op:"event-name"}'` returns null for every row; the
correct projection is `data[].{t:"event-time",op:data."event-name"}`.

**P8 — AD names carry a tenancy-specific prefix.** The shape is
`<four-letter tenancy prefix>:US-CHICAGO-1-AD-1` [verified live 2026-09-09; the prefix
itself is tenancy data and is not reproduced here]. It differs per tenancy, so AD names
are never portable — resolve with `oci iam availability-domain list --compartment-id "$T" --all
--query 'data[].name'`. Fault domains are the fixed `FAULT-DOMAIN-1..3`.

## 3. Capacity and limits

**P9 — Flex shapes need `--shape-config`.** Shapes ending in `.Flex` have no fixed
OCPU/memory; a launch without `--shape-config '{"ocpus":1,"memoryInGBs":6}'` (camelCase
keys, P7) fails. Generate the shape with `--generate-param-json-input shape-config`.

**P10 — Limits, quotas and availability are three different answers.** `limits value list`
= the Oracle-set service limit; `limits quota list` = a tenancy policy that can only lower
it (`effective-quota-value: null` means no quota applies); `limits resource-availability
get` = what is free right now. A capacity claim citing only one is wrong. Limits with no
availability API return **404 by design** [verified] — not an error to escalate.
`--availability-domain` is mandatory iff the limit's `scope-type` is `AD`, else a 400.

**P11 — `OutOfHostCapacity` is not a limit.** It means the AD has no hardware even when
`resource-availability get` shows headroom. Retry another AD or region; do not file a
limit-increase ticket.

## 4. Timing, naming and guard evasion

**P12 — 429 and silent retry.** The CLI retries by default — "For most commands, 7
attempts will be made. For operations with binary bodies, retries are disabled"
[verified — `--max-retries` help]. A command that "takes 40 s" may be backing off a 429.
For sweeps, serialize and add jitter rather than raising `--max-retries`.

**P13 — IAM eventual consistency.** A new policy, dynamic group, compartment or grant is
not instantly effective (allow ~1 min, longer cross-region). Creating a policy then
immediately testing it yields a spurious P3 404 — retry with backoff. A deleted
compartment lingers as `lifecycle-state: DELETING`.

**P14 — CLI names are not Console names.** "Kubernetes Engine (OKE)" → `oci ce`; "Block
Volume" → `oci bv`; "Object Storage" → `oci os`; "Networking/VCN" → `oci network`;
"Compute" splits into `oci compute` + `oci compute-management`; "Database" → `oci db`;
"Vault/KMS" → `oci kms` + `oci vault`; "Resource Manager" → `oci resource-manager`. 174
top-level groups exist in 3.91.0 — resolve with `scripts/catalog.py find`, never by guess.

**P15 — `raw-request` and `--from-json` defeat name-based guards.** A denylist keyed on
`oci <service> <resource> <verb>` misses `oci raw-request --http-method POST` entirely,
and `--from-json` can supply arguments a regex expected on the command line. Classify
`raw-request` by `--http-method` and resolve `file://` inputs before deciding. The
read-only wrapper does exactly this; never bypass it.

## Also verified live 2026-09-09
`ERROR: Profile 'NOPE' not found in config file <path>`;
`ERROR: No security_token_file was found in config for profile: DEFAULT` (an `api_key`
profile has no session to validate); and `RequestException` with
`"target_service": "CLI"`, `"request_endpoint": null` for `--region us-nowhere-1`.

## Links
[API errors](https://docs.oracle.com/en-us/iaas/Content/API/References/apierrors.htm) ·
[Service limits](https://docs.oracle.com/en-us/iaas/Content/General/Concepts/servicelimits.htm) ·
[Managing regions](https://docs.oracle.com/en-us/iaas/Content/Identity/Tasks/managingregions.htm) (200, 2026-09-08)
