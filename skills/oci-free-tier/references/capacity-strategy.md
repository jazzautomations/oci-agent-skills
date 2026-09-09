Purpose: what to do when an Always Free launch keeps failing, and how to tell hardware scarcity
from entitlement. Source: research/06c §2, §7 rules 1-3 and 15, research/12 A1, A5.
Verified 2026-09-09 on CLI 3.91.0, us-chicago-1.

## Contents
Three failure modes · The two gates · Retry discipline · PAYG · What a free tenancy cannot do

## Three failure modes
Separate these before advising anything; only two of the three are fixable by the user.

| Symptom | Meaning | Who fixes it |
|---|---|---|
| `Out of host capacity` (500 `InternalError`) | No hypervisor capacity for that shape in that AD right now | Nobody — wait and retry |
| `LimitExceeded` naming a shape or OCPU count | Oracle-set service limit, or the Always Free allotment | Support, via a limit request — and a free tenancy cannot file one |
| `QuotaExceeded` | A compartment **quota policy** written by your own admin | You, by editing the quota |

Out of host capacity is a queue, not a bug, and Oracle documents it as temporary Always-Free
scarcity in the home region. Report the failed launch accurately; a limit increase does not resolve physical scarcity.

## The two gates
A launch needs both entitlement and an offered shape, and they are read separately.

Gate 1 — entitlement, and whether it is spent:

```bash
oci limits resource-availability get --compartment-id "$TENANCY_ID" --service-name compute \
  --limit-name standard-a1-core-count --availability-domain "$AD" \
  --query 'data.{used:used,available:available,quota:"effective-quota-value"}'
```

`[verified]` this returned `available: 2, used: 0` for A1 in AD-1. Two rules come out of live
runs on this tenancy: the same call **without** `--availability-domain` fails with
`ServiceError ... code InvalidParameter, "Invalid parameter 'availabilityDomain'"` (400),
because every free compute limit reports `scope-type: AD`; and `available` can be **negative**
(`-4` against `vcn-count` 2, with 6 in use) when the tenancy already exceeds the allotment. A
404 from this call is a documented data gap for limits that do not support the API — degrade to
`oci limits value list` and say the usage figure is unavailable rather than inventing one.

Gate 2 — whether the shape is offered there at all:

```bash
oci compute shape list --compartment-id "$TENANCY_ID" --availability-domain "$AD" \
  --limit 100 --query 'data[?contains(shape,`A1`)||contains(shape,`Micro`)].shape'
```

`[verified]` in all three ADs this returned only `VM.Standard.A1.Flex` and `BM.Standard.A1.160`
— **no** `VM.Standard.E2.1.Micro`, even in the AD whose `standard-e2-micro-core-count` is 2. A
nonzero limit is not an offer. When gate 1 passes and gate 2 is empty, the shape is not being
offered in that AD and do not retry launches until shape availability changes.

## Retry discipline
- Rotate availability domains; A1 is allowed in every AD except South Korea North (Chuncheon)
  `[unverified]`, while the E2 micro allotment can be pinned to a single AD (proven above).
- Back off. The community answer is a polling script that hammers `LaunchInstance`; an agent
  implements exponential backoff with a ceiling and a stop condition, and tells the user this
  is a queue that can take days.
- Retrying is the only lever for capacity. Do not raise a limit request, do not change region
  (Always Free exists only in the home region), do not switch to a paid shape without saying
  so out loud and quoting the price.
- A launch is a mutation and is out of scope here. This skill reads the two gates and reports;
  the launch itself belongs to oci-compute and to the user's explicit approval.

## PAYG
Upgrading to Pay As You Go unlocks additional paid resource types while Always Free
allowances remain. A higher-priority A1 capacity pool is [unverified — community];
do not promise availability. Usage above free allowances becomes chargeable. The upgrade is asynchronous
and has been documented stalling for over a week `[unverified]`; verify by re-reading limits.

## What a free tenancy cannot do
- File a service-limit increase or any support request. Free Tier and Always-Free-only accounts
  are not eligible for Oracle Support; the channels are Support Chat and Cloud Customer Connect
  (oci-support-limits owns that ladder and the `validate-user` preflight).
- Build a private subnet with egress: `nat-gateway-count` is **0** `[verified]`.
- Exceed 2 VCNs, and the VCN Wizard consumes a whole one.
- Open outbound TCP 25 (tenancies from 2021-06-23 on), because the exemption is a limit request.
- Get a GPU: GPU limits start at 0, are per-region, and increases take 1-3 business days
  `[unverified]` — there is no weekend path.

Docs: https://www.oracle.com/cloud/free/faq/
· https://docs.oracle.com/en-us/iaas/Content/General/Concepts/servicelimits.htm
· https://docs.oracle.com/en-us/iaas/Content/GSG/support/getting-help.htm
