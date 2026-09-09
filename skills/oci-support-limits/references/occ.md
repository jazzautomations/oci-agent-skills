Purpose: the OCI Control Center capacity-contract surface — what it is, and why it is almost
always "not entitled" rather than "wrong compartment".
Source: research/11 §7; verified-on CLI 3.91.0, us-chicago-1, 2026-09-09.

## 1. What `oci capacity-management` is not

It is **not** service limits and it does **not** answer "why did my launch fail with Out of host
capacity". That question belongs to `oci limits` plus compute availability. OCC is the
large-customer capacity **contract** surface: availability catalogs Oracle publishes to a customer
group, capacity requests placed against them, handover resource blocks when the hardware lands,
and demand signals (forecasts you send Oracle). 57 operations in the group.

## 2. The entitlement gate

Every collection read on this tenancy returned **`NotAuthorizedOrNotFound`** — "Authorization
failed or requested resource not found" — for `occ-customer-group-collection list`,
`occ-availability-catalog-collection list`, `occ-capacity-request-collection list`,
`occ-handover-resource-block-collection list` and `occ-overview-collection list`
[verified, 2026-09-09]. OCC is visible only to tenancies enrolled in an OCC customer group, so
this is the normal answer for almost every tenancy.

**Read it as "not entitled", never as "wrong compartment", and never retry it against child
compartments** — that is a pointless sweep that only earns throttling.

## 3. Reads

```bash
oci capacity-management occ-customer-group-collection list --compartment-id "$TENANCY_ID" --limit 10 --query 'data.items[].{id:id,name:"display-name",status:status}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci capacity-management occ-availability-catalog-collection list --compartment-id "$TENANCY_ID" --limit 10 --query 'data.items[].{id:id,ns:namespace,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci capacity-management occ-availability-collection list --occ-availability-catalog-id "$CATALOG_ID" --limit 20 --query 'data.items[].{shape:"resource-name",date:"date-final-customer-order",qty:"available-quantity"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci capacity-management occ-capacity-request-collection list --compartment-id "$TENANCY_ID" --limit 20 --query 'data.items[].{id:id,state:"lifecycle-state",ns:namespace}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci capacity-management occ-overview-collection list --compartment-id "$TENANCY_ID" --namespace COMPUTE --limit 20 --query 'data.items[]' --profile "$PROFILE" --region "$REGION"
```

Order of use: customer group -> catalog -> the availability rows inside that catalog -> your
outstanding requests. `--namespace` here is the **OCC** namespace (e.g. `COMPUTE`), unrelated to
Object Storage or Monitoring namespaces.

## 4. Boundaries

- The 13 `*-internal` and `internal-demand-signal` leaves are Oracle-side operator commands; a
  customer principal cannot call them. Keep them out of every command list.
- `occ-availability-catalog get-catalog-content` requires `--file` and writes the catalog to
  local disk. Treat the destination like any other artifact: it is contract data.
- `demand-signal occm-demand-signal list -c <tenancy>` shows forecasts already submitted to
  Oracle. Submitting one is a commercial commitment — propose, never send.

Doc (HTTP 200, 2026-09-09):
https://docs.oracle.com/en-us/iaas/Content/control-center/home.htm ·
https://docs.oracle.com/en-us/iaas/tools/oci-cli/latest/oci_cli_docs/cmdref/capacity-management.html
