Purpose: put a cap and an alarm on spend, and know what a budget cannot do.
Source: research/09c B4/B5, research/04b §18; verified-on CLI 3.91.0, us-chicago-1, 2026-09-09.

## 1. The doubled noun

The command is `oci budgets budget budget ...`, not `oci budgets budget ...`. `oci budgets` has
subgroups `budget` and `cost-ad`; `oci budgets budget` has subgroups `alert-rule` and `budget`
[verified, help]. Scripts and agents get this wrong routinely.

```bash
oci budgets budget budget list --compartment-id "$TENANCY_ID" --limit 50 --query 'data[].["display-name",amount,"actual-spend","forecasted-spend"]' --profile "$PROFILE" --region "$REGION"
```

```bash
oci budgets budget alert-rule list --budget-id "$BUDGET_ID" --limit 20 --query 'data[].[type,threshold,"threshold-type"]' --profile "$PROFILE" --region "$REGION"
```

The first returned an empty list in this tenancy [verified, executed 2026-09-09]; the second is
`[shape-verified]` only, because there is no budget here to supply `--budget-id`. **An empty
budget list is a finding, not a pass** — it means nothing is watching the bill.

## 2. Creating one (the user runs this, not the agent)

```bash
# MUTATING — not run in this repo; [shape-verified] against CLI 3.91.0 --help
# rollback: oci budgets budget budget delete --budget-id "$BUDGET_ID" --force --profile "$PROFILE" --region "$REGION"
oci budgets budget budget create --compartment-id "$TENANCY_ID" --amount 500 --reset-period MONTHLY --target-type COMPARTMENT --targets '["'"$TARGET_COMPARTMENT_ID"'"]' --display-name dev-monthly --query 'data.id' --profile "$PROFILE" --region "$REGION"
```

```bash
# MUTATING — not run in this repo; [shape-verified] against CLI 3.91.0 --help
# rollback: oci budgets budget alert-rule delete --budget-id "$BUDGET_ID" --alert-rule-id "$ALERT_RULE_ID" --force --profile "$PROFILE" --region "$REGION"
oci budgets budget alert-rule create --budget-id "$BUDGET_ID" --type ACTUAL --threshold 80 --threshold-type PERCENTAGE --recipients finops@example.com --message "dev budget at 80%" --query 'data.id' --profile "$PROFILE" --region "$REGION"
```

Semantics that bite [verified, help, research/09c B4]:

- `--reset-period` accepts **only** `MONTHLY`.
- `--target-type` is `COMPARTMENT` **or** `TAG` and cannot be mixed in one budget. The tag form
  targets a cost-tracking tag: `--target-type TAG --targets '["Finance.CostCenter.platform"]'`.
- `--target-compartment-id` is **deprecated**; use `--targets`.
- `--processing-period-type` is `INVOICE|MONTH|SINGLE_USE`, with
  `--budget-processing-period-start-offset` for non-calendar billing months.
- Alert `--type` is `ACTUAL` (already spent) or `FORECAST` (projected). A mature setup has both:
  `FORECAST` at 100% catches the month before it happens, `ACTUAL` at 80% and 100% confirm it.
- `--recipients` is a comma list; an empty string means null.

## 3. Budgets alert; they do not stop anything

Nothing in `budgets` prevents spend. The only OCI mechanism that refuses the request is a
**compartment quota** — a policy in the root compartment targeting a child, with the verbs
`set`, `unset` and `zero`. Quotas are evaluated at request time, so one added later never
reclaims what already exists [verified, research/09c B5]. Service limits are Oracle's ceiling
and belong to the support-limits skill; quotas are yours and sit below it.

## 4. Anomaly detection

`oci budgets cost-ad` adds `cost-anomaly-monitor`, `cost-anomaly-event` and
`cost-alert-subscription` — a spike catcher for what a fixed threshold misses [verified, help].
Reading it here returned `NotAuthorizedOrNotFound`, 404 [verified, executed 2026-09-09]: on a
tenancy that never enabled the feature that is the expected answer, and sweeping child
compartments looking for it wastes calls and tells you nothing.

## 5. The free-tier guard

One `MONTHLY` budget of a small amount on the tenancy plus a `FORECAST` alert at 1%: on a
tenancy that should cost nothing, any nonzero forecast means something escaped the free
allotment [research/04b §18]. Cheap, and it fires before the invoice does.

Docs (HTTP 200, 2026-09-09):
https://docs.oracle.com/en-us/iaas/Content/Billing/Concepts/budgetsoverview.htm ·
https://docs.oracle.com/en-us/iaas/Content/Quotas/Concepts/resourcequotas.htm
