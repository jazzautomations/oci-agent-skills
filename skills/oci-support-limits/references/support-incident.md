Purpose: decide whether a support request is even possible, then build one that will not be
rejected or leak secrets.
Source: research/12 A1–A4, A6; verified-on CLI 3.91.0, us-chicago-1, 2026-09-09.

## 1. The eligibility gate — check it first, every time

Support requests are **paid accounts only**. Customers using only Always Free resources, and Free
Tier accounts, are not eligible for Oracle Support [doc]. For those tenancies the whole ladder is
community: Cloud Customer Connect
(https://community.oracle.com/customerconnect/categories/oracle-cloud-infrastructure-and-platform),
the `oracle-cloud-infrastructure` Stack Overflow tag, and Support Chat / "Ask Oracle" in the
Console **Help** menu. `https://support.oracle.com` and the `oci support` CLI are paid-only [doc].

`validate-user` is the cheap read-only preflight and it fails closed. Live on this
tenancy 2026-09-09 [verified]: **403 `AUTHZ_FAILED`** ("Authorization failed for the request
input") against `incidentmanagement.us-chicago-1...`; pinned to `us-phoenix-1` the same call
returns **401 `NotAuthenticated`**. `incident-resource-type list` returns the same 403 [verified].
These historical statuses do not establish the cause: 403 alone does not prove
missing entitlement, and 401 alone does not prove an unsubscribed region.
Verify the selected user, home region, identity domain, Support onboarding,
user-group privileges and IAM policy. Keep the read failed until access succeeds.

The call is `oci support validation-response validate-user --problem-type TECH --ocid "$USER_ID"
--homeregion "$HOME_REGION"`, plus `--profile` and `--region`. It is not shown as a runnable
fence here on purpose: `validate-user` is a GET, but its verb is outside the D3 read-only verb
allowlist, so `scripts/lib/oci_ro` — and therefore every plugin script — refuses it. Run it
yourself; never wrap it in a script. A 200 returns the **eligible user groups**; use those and
never invent one.

## 2. Identity plumbing

- The IAM user needs an email address; the Console provisions the support account on first use [doc].
- **User groups, not CSI, are the authorization unit.** `oci support incident create --help` on
  3.91.0 exposes no `--csi` option at all [verified]; guidance to collect a CSI is stale for this
  CLI generation. Ask the Customer User Administrator for create privileges in a user group [doc].
- `--ocid` (user OCID) is mandatory for OCI users; `--domainid` is **mandatory for a non-default
  identity domain**; `--homeregion` is the tenancy's home region [verified].
- Linking a support account is a Console/identity **write** and out of scope here.

## 3. Problem types and severity

`--problem-type` enum: `LIMIT|LEGACY_LIMIT|TECH|ACCOUNT|TAXONOMY` [verified]. `TECH` for a fault,
`ACCOUNT` for billing/account, `LIMIT` only as the legacy limit path — a normal limit raise goes
through `oci limits-increase`. `--user-group-id` applies to `TECH` only [verified].

`--severity` enum: `LOW|MEDIUM|HIGH|HIGHEST` — all four accepted on 3.91.0 [verified]; guidance
that `LOW` is missing applies to older CLIs. `HIGHEST` = Sev 1 critical outage and the help text
states the obligation verbatim: "Oracle Support requires a 24x7 contact be provided so additional
information can be requested as needed 24x7" [verified]. `HIGH` = severe loss with no workaround,
`MEDIUM` = minor loss with a workaround, `LOW` = question or cosmetic.

**Severity comes from confirmed current operational impact, never from how fast the user wants an
answer, and the user confirms it before submission.** Never let a model pick it silently.

`--referrer` is worth filling: it carries the Console deep link the user was on, which is exactly
what the shared console-links reference builds.

## 4. Taxonomy and tracking reads

```bash
oci support incident-resource-type list --compartment-id "$TENANCY_ID" --problem-type TAXONOMY --ocid "$USER_ID" --limit 20 --query 'data.items[].{name:name,key:key}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci support incident list --compartment-id "$TENANCY_ID" --ocid "$USER_ID" --limit 20 --query 'data[].{key:key,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

Both returned 403 on this tenancy 2026-09-09 [verified], with two different codes worth keeping
apart: `incident-resource-type list` -> `AUTHZ_FAILED`, `incident list` -> `USER_POLICY_NOT_AUTHORIZED`
("User policy is not authorized. HttpStatus 403"). Review the §1 eligibility and
§2 identity/authorization checks; these codes alone do not determine the root cause.
Note a support request is keyed by an **incident key**, not an OCID.

## 5. Writes (all `[shape-verified]`, none executed here)

```bash
# MUTATING — not run in this repo; [shape-verified] against CLI 3.91.0 --help
# rollback: NONE — an SR cannot be deleted; close it in the Console or with `incident update`
oci support incident create --compartment-id "$TENANCY_ID" --problem-type TECH --severity MEDIUM --title "$TITLE" --description "$DESCRIPTION" --ocid "$USER_ID" --homeregion "$HOME_REGION" --user-group-id "$USER_GROUP_ID" --query 'data.key' --profile "$PROFILE" --region "$REGION"
```

```bash
# MUTATING — not run in this repo; [shape-verified] against CLI 3.91.0 --help
# rollback: NONE — a posted comment cannot be withdrawn
oci support incident update --compartment-id "$TENANCY_ID" --incident-key "$INCIDENT_KEY" --activity-type UPDATE --type activity --comments "$COMMENT" --if-match "$ETAG" --query 'data.key' --profile "$PROFILE" --region "$REGION"
```

Always pass a fresh `--if-match` ETag on `update` and never `--force`. Attachments go through
`put-attachment`: review every file for wallets, private keys, auth tokens, CHAP secrets and raw
instance metadata **before** attaching, and never run `--debug` while collecting evidence — it
prints request-signing detail into the bundle (research/12 A6).

Docs (HTTP 200, 2026-09-09):
https://docs.oracle.com/en-us/iaas/Content/GSG/support/getting-help.htm ·
https://docs.oracle.com/en-us/iaas/Content/GSG/support/validate-user.htm

Account prerequisites rechecked 2026-09-11:
https://docs.oracle.com/en-us/iaas/Content/GSG/Tasks/usingsupport.htm
