Purpose: decide which of the three walls the user actually hit before anyone files anything.
Sources: Oracle CLI/API contracts and the official documentation linked below.
Corrected 2026-09-13 against CLI 3.91.0 help and SDK 2.185.0 models. Earlier
2026-09-09 observations remain historical; no new live reads accompanied this correction.

## 1. The three walls

| Wall | Who sets it | How it reads | Who can move it |
|---|---|---|---|
| **Service limit** | Oracle, per tenancy/region/AD | `limits value list` | a limit-increase request |
| **Compartment quota** | administrators, through quota policies | `limits quota list` | an authorized policy update |
| **Physical capacity** | available hardware for the requested placement | Compute capacity information/reservations or an actual placement result | placement choices and available supply |

A quota cannot raise a service limit. Both service limits and quotas can prevent
resource creation; budgets provide tracking/alerts and do not reserve resources.
`resource-availability get` reports limit/quota usage and headroom for its
**requested compartment**, not free hardware. A returned effective quota describes
that compartment and the selected region/AD, not every compartment in the tenancy.
Use fractional usage/availability fields when present; the integer fields round.

## 2. Order of operations

1. Resolve the service's programmatic name and the exact limit name. Use a bounded
   metadata read under the explicitly selected tenancy.
2. Filter `limits definition list` by `--service-name` and `--name`; inspect the
   returned `scope-type` (`GLOBAL|REGION|AD`). Do not infer scope from a shape name.
3. Read that limit's configured value, matching its scope and AD where applicable.
4. Read `limits resource-availability get` under the **target compartment**. A
   tenancy-wide read cannot establish a child's effective quota or usage.

For `AD`, require the requested availability domain. For `REGION` or `GLOBAL`,
omit `--availability-domain`, even if an unrelated AD is set in the environment.
Missing, ambiguous, truncated or unsupported scope metadata is a reason to stop
and report the gap, not to guess. A dynamic-limit flag does not promise that an
increase will arrive in time for the user's workload.

The [capacity helper](../scripts/capacity.sh) implements these bounded reads.
It requires `PROFILE`, `REGION`, `TENANCY_ID`, `COMPARTMENT_ID`, `SERVICE` and
`LIMIT_NAME`; `AD` is conditional. Its single JSON report separates configured
values from compartment headroom and explicitly leaves physical capacity unverified.

## 3. Reads

```bash
oci limits service list --compartment-id "$TENANCY_ID" --query 'data[].name' --profile "$PROFILE" --region "$REGION" --limit 20
```

```bash
oci limits quota list --compartment-id "$TENANCY_ID" --limit 20 --query 'data[].{name:name,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

Quota policies belong to a selected compartment and can target compartments using
`set`, `unset` and `zero`. The example below deliberately uses the tenancy; that is
not a requirement for every quota policy. New policies can take up to ten minutes
to take effect and do not reclaim existing resources. Writing one is a mutation:

```bash
# MUTATING — not run in this repo; [shape-verified] against CLI 3.91.0 --help
# rollback: oci limits quota delete --quota-id "$QUOTA_ID" --force --profile "$PROFILE" --region "$REGION"
oci limits quota create --compartment-id "$TENANCY_ID" --name no-gpu-in-dev --description "block GPU shapes in dev" --statements '["Zero compute quota /gpu-shapes/ in compartment dev"]' --query 'data.id' --profile "$PROFILE" --region "$REGION"
```

## 4. Reading the answer back to the user

- Positive headroom rules out neither authorization problems nor image, network,
  placement or other prerequisite failures. Diagnose the actual error.
- For a confirmed out-of-host-capacity error, review shape/AD/fault-domain
  alternatives within the user's authorized scope. Do not launch in a retry loop
  or promise that a paid-account upgrade guarantees capacity.
- List only shapes returned by the scoped shape listing. An existing VM's shape,
  a price catalog entry or a service-limit name is not an additional listing result.
- Free-tier eligibility, current pricing and actual capacity are separate; use
  the free-tier skill for the current allowance contract. Do not promise universal
  GPU limits, provisioning timelines or reservation availability.
- Some limits lack availability data. For a 404, retain the permission/resource
  ambiguity and check whether that limit supports the API. A configured limit value
  alone does not establish usage; unavailable measurements remain unknown, not zero.

Official references (reviewed 2026-09-13):
https://docs.oracle.com/en-us/iaas/Content/General/Concepts/servicelimits.htm ·
https://docs.oracle.com/en-us/iaas/Content/Quotas/Concepts/resourcequotas.htm ·
https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/troubleshooting-out-of-host-capacity.htm ·
https://docs.oracle.com/en-us/iaas/tools/oci-cli/latest/oci_cli_docs/cmdref/limits/resource-availability/get.html
