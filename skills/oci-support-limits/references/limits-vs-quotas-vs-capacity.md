Purpose: decide which of the three walls the user actually hit before anyone files anything.
Source: research/12 A5, research/04a §2.10, research/09c B5, research/06c §2; verified-on CLI 3.91.0, us-chicago-1, 2026-09-09.

## 1. The three walls

| Wall | Who sets it | How it reads | Who can move it |
|---|---|---|---|
| **Service limit** | Oracle, per tenancy/region/AD | `limits value list` | a limit-increase request |
| **Compartment quota** | you, as tenancy policy | `limits quota list` | you, immediately |
| **Physical capacity** | nobody | `resource-availability get`, or the launch itself | nothing but time |

A quota can only lower a service limit, never raise it. `effective-quota-value: null` in a
`resource-availability get` response means no quota policy applies to that limit [verified]. Only
quotas actually **prevent** consumption; limits and budgets report it (research/09c B5).

## 2. Order of operations

1. `limits service list` -> the programmatic service name (`compute`, not "Compute"). 128 services
   on this tenancy [verified]; `ai-anomaly-detection` is still a limits service name although the
   CLI group was removed in 3.65.0 [verified].
2. `limits definition list --service-name <svc>` -> read **`scope-type`** (`GLOBAL|REGION|AD`) and
   `is-dynamic` for the exact limit.
3. `limits value list` -> the configured number, per AD when AD-scoped.
4. `limits resource-availability get` -> `used`, `available`, `effective-quota-value`.

**Never skip step 2.** Every `*-e4-*` and `*-e5t-*` compute limit is `"scope": "AD"` [verified], and
an AD-scoped limit read without `--availability-domain` fails with a bare
`InvalidParameter: Invalid parameter 'availabilityDomain'`, status 400 [verified, reproduced
2026-09-09]. Adding the AD returns `{"available":0,"used":0,...}` for the same limit [verified].
The converse also holds live: `custom-image-count` is `REGION`-scoped and reads fine with no AD
at all [verified, 2026-09-09] — so do not pass one blindly either.

A **dynamic** limit grows with consumption on its own — check `is-dynamic` before advising a
request, or you file a ticket for something that was going to fix itself (research/12 A5 [doc]).

## 3. Reads

```bash
oci limits service list --compartment-id "$TENANCY_ID" --query 'data[].name' --profile "$PROFILE" --region "$REGION" --limit 20
```

```bash
oci limits quota list --compartment-id "$TENANCY_ID" --limit 20 --query 'data[].{name:name,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

Quotas live in the **root** compartment and target children (`in compartment dev`); the verbs are
`set`, `unset` and `zero`, and they are evaluated at request time, so a quota added later never
reclaims what already exists (research/09c B5). Writing one is a mutation:

```bash
# MUTATING — not run in this repo; [shape-verified] against CLI 3.91.0 --help
# rollback: oci limits quota delete --quota-id "$QUOTA_ID" --force --profile "$PROFILE" --region "$REGION"
oci limits quota create --compartment-id "$TENANCY_ID" --name no-gpu-in-dev --description "block GPU shapes in dev" --statements '["Zero compute quota /gpu-shapes/ in compartment dev"]' --query 'data.id' --profile "$PROFILE" --region "$REGION"
```

## 4. Reading the answer back to the user

- `available > 0` and the launch still fails -> physical capacity, not a limit. `Out of host
  capacity` is a 500 with `InternalError`, endemic to Always-Free A1/ARM in the home region.
  The community fix is a backoff retry loop, not a ticket; the real fix is upgrading to PAYG,
  which keeps every Always Free allowance at $0 but moves the tenancy to a higher-priority pool
  (research/06c §2 [doc]).
- Always Free shapes exist **only in the home region** — subscribing to another region does not
  make them appear there (research/06c §2 [doc]).
- GPU limits start at **0** in a new tenancy and are per-region; A100/H100/L40S are largely
  reservation-only and an increase runs 1–3 business days, so there is no weekend GPU
  (research/06c §2 [doc]).
- A 404 from `resource-availability get` means that limit does not support the availability API —
  a documented data gap, not a broken command [verified, help text]. Degrade to `value list` and
  say the usage figure is unavailable rather than reporting zero usage.

Docs (HTTP 200, 2026-09-09):
https://docs.oracle.com/en-us/iaas/Content/General/Concepts/servicelimits.htm ·
https://docs.oracle.com/en-us/iaas/Content/Quotas/Concepts/resourcequotas.htm ·
https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/troubleshooting-out-of-host-capacity.htm
