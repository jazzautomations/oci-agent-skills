Purpose: the recurring reasons an OCI bill is bigger than the architecture diagram suggests.
Source: research/06c §5, §9, §10; verified-on CLI 3.91.0, us-chicago-1, 2026-09-09.

## 1. Things that keep billing after you deleted the thing

- **Boot volumes outlive their instances.** Terminating an instance does not delete its boot
  volume unless the box was ticked. Orphans bill at $0.0425/GB-mo (Balanced) forever. Audit with
  `oci bv boot-volume list` [verified, research/06c §5].
- **Volume backup policies keep firing.** A Bronze/Silver/Gold policy goes on creating billable
  backups after the source volume is gone. Audit with `oci bv backup list` [verified].
- **Uncommitted multipart uploads.** A failed large `oci os object put` leaves parts that appear
  in **no** bucket listing but do appear on the invoice, and nothing cleans them up. Audit with
  `oci os multipart list --bucket-name ...`; fix permanently with an Object Lifecycle rule
  [verified].
- **Stopped is not free.** Stopping a VM stops OCPU and memory billing and nothing else: boot
  volume, block volumes, reserved public IPs and load balancers keep charging [research/06c §5].

## 2. Multipliers people forget

- **VPU is a hidden 1.67x.** Everyone quotes $0.0255/GB-mo for Block Volume; the default
  Balanced tier adds 10 VPU at $0.0017 each, so the real number is $0.0425/GB-mo. Higher
  Performance (20 VPU) is $0.0595 [verified via the price API].
- **Windows is ~3.7x the OCPU price.** The B88318 uplift is +$0.092/OCPU-hr on top of the shape,
  so the same 2-OCPU VM roughly triples the compute line [verified].
- **Egress is asymmetric by continent.** Past the 10 TB/month free allowance: $0.0085/GB from
  NA/EU/UK, **$0.025/GB from South America and APAC**, $0.05/GB from MEA. Serving Brazilian
  users from a Brazilian region is ~3x the North American rate [verified].
- **File Storage is ~12x Block Volume** — $0.30/GB-mo against $0.0255 [verified]. Reaching for
  FSS because it is convenient is a real decision, not a neutral one.

## 3. Step functions: the second one is never free

The costly changes are discrete, which is why a single estimate is always wrong:

| Change | Delta |
|---|---|
| A **second** load balancer (blue/green, or a 2nd region) | +$8.25/mo — 744 free LB-hr covers exactly one |
| Boot volume to Higher Performance (20 VPU) | +$1.70/mo per 100 GB |
| The same VM on **Windows** | +$134.32/mo for 2 OCPU |
| **OKE Enhanced** cluster instead of Basic | +$73.00/mo for the control plane alone |
| Self-managed DB to **Autonomous AI TP, 2 ECPU** | +$490.56/mo (BYOL +$117.82) |
| A **Virtual Private Vault** | **+$2,718.52/mo** |

The Virtual Private Vault (B90328, $3.724/vault-hr) is the largest single accidental spend an
agent can cause: creating one "to be tidy" instead of using the shared default vault costs more
than the rest of a small stack put together [verified via the price API].

## 4. Account-shaped surprises

- The classic complaint is being moved off Always Free during signup, then charged ~EUR 60-80/mo
  for a shape that looked free, with charges continuing after the instance was stopped and
  deleted [research/06c §5, community reports — `[unverified]` as a mechanism, but the boot
  volume and reserved-IP behaviour above explains most of it].
- Free Tier and Always Free are unavailable in US Government Cloud regions, and Always Free
  compute and ADBs exist **only in the home region** — subscribing to another region does not
  make them appear there [doc].

## 5. The audit order

1. `usage-api` MONTHLY grouped by `service`, then DAILY grouped by `service` and `skuName` over
   the window where the total moved. The SKU name is what identifies the trap.
2. Match the SKU to §1-§3 here before touching any resource.
3. Only then list the resources: boot volumes, backups, multipart uploads, load balancers,
   vaults, and anything Windows.
4. Set a budget with a `FORECAST` alert so the next one arrives as a notification, not an
   invoice.

Docs (HTTP 200, 2026-09-09):
https://docs.oracle.com/en-us/iaas/Content/Block/Concepts/bootvolumes.htm ·
https://docs.oracle.com/en-us/iaas/Content/Object/Tasks/To_delete_uncommitted_multipart_uploads.htm ·
https://docs.oracle.com/en-us/iaas/Content/Billing/Concepts/budgetsoverview.htm
