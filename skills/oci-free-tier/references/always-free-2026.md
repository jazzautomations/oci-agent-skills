Purpose: what an OCI tenancy actually gets for $0 in 2026, and how to confirm it from the
tenancy instead of quoting a doc. Source: research/04b §15, research/06c §1, §7.
Verified 2026-09-09 on CLI 3.91.0 against a Free-Tier tenancy in us-chicago-1.

## Contents
Reading it live · Compute · Storage · Database · Network · Other · Traps

## Reading it live
Docs go stale; the tenancy does not. `oci limits value list` is the entitlement of record, and
`--name` filters server-side, but the explicit page cap still applies:

```bash
oci limits value list --compartment-id "$TENANCY_ID" --service-name compute \
  --name standard-a1-core-count --limit 100 \
  --query 'data[].{n:name,v:value,ad:"availability-domain"}'
```

`oci limits service list --compartment-id "$TENANCY_ID" --limit 200` gives the service names
these calls take (128 on the reference tenancy). Values are per **region**, and Always Free
only exists in the home region, so a value read in a subscribed region says nothing about it.

## Compute
- `VM.Standard.A1.Flex` (Ampere): **1,500 OCPU-hours and 9,000 GB-hours per month**, i.e.
  2 OCPUs and 12 GB, splittable 1x2 or 2x1. Halved from 4/24 in 2026 with no announcement;
  the price-list API still encodes the old tier (`B93297` rangeMax 3000) `[unverified]`.
  Never promise the old numbers.
- 2x `VM.Standard.E2.1.Micro` (AMD, 1/8 OCPU burstable, 1 GB, 1 VNIC, 1 public IP).
- Live shape of that entitlement, us-chicago-1, `[verified]`: `standard-a1-core-count` = **2 in
  every AD**, while `standard-e2-micro-core-count` = **2 in AD-2 and 0 in AD-1 and AD-3**. The
  micro allotment is pinned to one AD; A1 is not. Both limits report `scope-type: AD` and
  `is-dynamic: false`.
- Minimum boot volume 47 GB on A1 (a live boot volume here is exactly 47 GB `[verified]`).
- Always-Free images: Oracle Linux, Oracle Linux Cloud Developer (needs >=8 GB on A1), Ubuntu,
  CentOS (E2 only).

## Storage
- Block + boot: **200 GB total**, 5 backups. Live `[verified]`: `total-free-storage-gb` = 200
  per AD, `total-free-storage-gb-regional` = 200, `free-backup-count` = 5 under service
  `block-storage`. Volumes outside the home region bill normally.
- Object + Archive: 50,000 API requests/month. An Always-Free-only account gets **20 GB
  combined**; live `[verified]`, service `object-storage`, `storage-bytes` = `21474836480`
  (20 GiB). A paid or trial account instead gets 10 GB Standard + 10 GB Infrequent + 10 GB
  Archive.
- Vault: software key versions unlimited, 20 HSM key versions, 150 secrets. A **virtual
  private vault is not free** and costs about $2,719/month `[unverified]` — never create one
  "to be tidy".

## Database
- 2x Always Free Autonomous Database (1 OCPU, 20 GB, max 20 sessions). Live `[verified]`:
  service `database`, `adb-free-count` = 2. Availability varies by home region.
- NoSQL 133M reads + 133M writes/month, 3 tables x 25 GB. MySQL HeatWave: one standalone
  system + single-node cluster, 50 GB data + 50 GB backup.

## Network
- **2 VCNs** on a free tenancy. Live `[verified]`: service `vcn`, `vcn-count` = 2,
  `internet-gateway-count` = 1, `nat-gateway-count` = **0**, `reserved-public-ip-count` = 1.
  A free tenancy therefore cannot build the private-subnet-plus-NAT topology at all, and the
  VCN Wizard consumes an entire VCN.
- Load balancer: live `[verified]` `lb-flexible-count` = 1 with `lb-flexible-bandwidth-sum` =
  10 (Mbps), 16 listeners / 16 hostnames / 16 backend sets — the post-2020-12-15 profile.
  Tenancies created before that date get a 10 Mbps Micro LB instead.
- Network Load Balancer: 1. Site-to-Site VPN: up to 50 IPSec connections.
- **Outbound TCP 25 is blocked** for every tenancy created on or after 2021-06-23. No security
  list, NSG or route table can open it; the only path is a limit-increase exemption, and a free
  tenancy cannot file one. Use Email Delivery on 587 or 465 (3,000 messages/month free).
- Outbound data transfer: 10 TB/month.

## Other
APM 1,000 tracing events + 10 synthetic runs per hour · Connector Hub 2 · Monitoring 500M
ingestion and 1B retrieval datapoints · Notifications 1M HTTPS + 1,000 email · Email Delivery
3,000/month · Bastion free on free and paid accounts · Resource Manager 100 stacks, 2
concurrent jobs.

## Traps
1. A limit value is entitlement, not availability. `standard-e2-micro-core-count` = 2 in AD-2
   while `oci compute shape list --availability-domain <AD-2>` returns no `Micro` shape at all
   `[verified]` — only `VM.Standard.A1.Flex` and `BM.Standard.A1.160`. Check both gates.
2. `resource-availability get` can return a **negative** `available`. Live `[verified]`:
   `vcn-count` used 6, available **-4**, against a limit of 2. Negative is not an error; it
   means the tenancy is already over the allotment and the next create will fail.
3. Always Free is per-tenancy and home-region-only, and is unavailable in US Government Cloud
   regions.
4. Upgrading to PAYG keeps every allotment at $0; only usage above them bills.
5. Values are read with the **tenancy** OCID. A child compartment returns a different, smaller
   picture and invites a wrong conclusion.

Docs: https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm
· https://docs.oracle.com/en-us/iaas/Content/FreeTier/resourceref.htm
