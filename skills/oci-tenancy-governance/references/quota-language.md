# Quotas, limits and budgets — three different things
Source: research/04b §11, research/09c B4 and B5; verified-on OCI CLI 3.91.0, 2026-09-09.

| Mechanism | Who sets it | Effect |
|---|---|---|
| **Service limit** | Oracle, per tenancy/region/AD | hard ceiling, read-only, raised by a support request |
| **Compartment quota** | you, in a declarative language | the **only** OCI mechanism that prevents spend |
| **Budget** | you, per compartment or cost-tracking tag | **alerts only** — it never blocks anything |

Never answer "cap our spend" with a budget alone. Service limits always take precedence over
quotas: a quota above the limit is legal and inert.

## Quota statement grammar
`<action>` + service family (`compute-core`, `database`, `email-delivery`, `notifications`)
+ `quota`/`quotas` + quota name (`standard-e4-core-count`, or a wildcard `/*exadata*/`)
+ (for `set`) `to <value>` + `in tenancy | in compartment <name[:child:...]>`
+ optional `where request.region = '<region>'` or `where request.ad=<ad>`.

Actions: `set` (a maximum), `unset` (back to the service limit), `zero` (no access at all).

```
Zero email-delivery quotas in compartment MyCompartment
set database quota /*exadata*/ to 1 in tenancy
set compute-core quota standard-e4-core-count to 240 in compartment MyCompartment where request.region = us-phoenix-1
set compute-core quota standard2-core-count to 20 in compartment MyCompartment where request.ad=abcd:US-PHOENIX-1-AD-1
unset compute-core quota standard2-core-count in compartment productionApp
zero compute-core quotas in tenancy
set  compute-core quota standard-e4-core-count to 240 in tenancy
```
The last pair is the allowlist idiom: zero the family, then grant back explicitly.

## Semantics that bite
- Only `request.region` and `request.ad` are supported conditionals, and quota policies use
  the **full region name** (`us-phoenix-1`), never the 3-letter IAM key (`PHX`).
- AD-scoped quotas are **per AD**: `to 120` means 120 in each AD, not 120 total.
- Sub-compartment usage counts toward the parent's usage.
- Within one policy, a later statement supersedes an earlier one on the same resource;
  across policies the most restrictive wins. The compartment the policy lives in does not
  affect precedence — quotas live in the tenancy root and *target* children by name.
- Quotas are evaluated at request time, so adding one never reclaims existing resources.
- `addlock`/`removelock` protect a quota from accidental deletion; a lock surfaces later as
  `ResourceLocked` on delete.

## Limits and capacity, read-only
`oci limits service list`, `oci limits value list --service-name <s>`,
`oci limits definition list` and `oci limits resource-availability get` all ran live
2026-09-09. Two observations worth carrying: `ai-anomaly-detection` is still a limits
*service name* although the CLI group was removed in 3.65.0, and `limits value list` returns
`AD`-scoped rows with `v: 0` for shapes the tenancy simply cannot use — a zero limit is not
an outage. Both `limits service list` and `limits value list` printed, on stderr,
`WARNING: This operation supports pagination and not all resources were returned.  Re-run
using the --all option to auto paginate and list all resources.` — treat a bounded read as a
sample, not an inventory, and read that warning as data about your page, not about the tenancy.

## Budgets
The noun is doubled: `oci budgets budget budget list|create`, because `oci budgets` has
subgroups `budget` and `cost-ad`, and `oci budgets budget` has `alert-rule` and `budget`.
`--target-type` is `COMPARTMENT` or `TAG` and cannot be mixed inside one budget;
`--reset-period` accepts only `MONTHLY`; `--processing-period-type` is
`INVOICE|MONTH|SINGLE_USE`. Alert `--type` is `ACTUAL` or `FORECAST`; a mature setup uses
both (FORECAST 100% plus ACTUAL 80%/100%). For spikes a fixed threshold misses, Cost Anomaly
Detection (`oci costad`) is the adjacent service.

Docs: https://docs.oracle.com/en-us/iaas/Content/Quotas/Concepts/resourcequotas.htm ·
syntax: https://docs.oracle.com/en-us/iaas/Content/Quotas/Concepts/quota_policy_syntax.htm ·
samples: https://docs.oracle.com/en-us/iaas/Content/Quotas/Concepts/sample_quotas.htm ·
budgets: https://docs.oracle.com/en-us/iaas/Content/Billing/Concepts/budgetsoverview.htm
