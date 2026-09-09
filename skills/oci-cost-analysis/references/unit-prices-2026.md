Purpose: the figures to quote when someone wants a number now, with their part numbers.
Source: research/06c §9, pulled live from the Price List API; snapshot `lastUpdated`
2026-09-01T14:26:53.943Z, USD, model `PAY_AS_YOU_GO` [verified]. Re-confirm with
`scripts/price.sh` before quoting — this file is a cache, not the source.

## Contents
1. Compute · 2. Storage · 3. Egress and networking · 4. Database · 5. Containers and
observability · 6. Two worked stacks

## 1. Compute (per hour)

| Shape | Part (OCPU / mem) | OCPU/hr | Mem GB/hr |
|---|---|---|---|
| **A1 (Ampere Arm)** | B93297 / B93298 | **$0 to 3,000 OCPU-hr/mo**, then $0.01 | **$0 to 18,000 GB-hr/mo**, then $0.0015 |
| E3 | B92306 / B92307 | $0.025 | $0.0015 |
| **E4** | B93113 / B93114 | **$0.025** | $0.0015 |
| **E5** | B97384 / B97385 | **$0.03** | $0.002 |
| E6 | B111129 / B111130 | $0.03 | $0.002 |
| X9 (Intel) | B94176 / B94177 | $0.04 | $0.0015 |
| Windows uplift | B88318 | **+$0.092** | — |

The A1 tier *is* the Always Free allowance, expressed inside the paid price list. The Windows
uplift is ~3.7x the E4 OCPU price and is the classic bill shock.

**GPU, per GPU-hr:** A10 $2.00 (B95909) · A100-80 v2 $4.00 (B95907) · L40S $3.50 (B109479) ·
H100 $10.00 (B98415) · H200 $10.00 (B110519) · MI300X $6.00 (B109485) · B200 $14.00 (B110978) ·
GB200 $16.00 (B110979) · GB300 $18.00 (B112140). The NVIDIA AI Enterprise licence bills
**separately on top**: H100 +$2.50/GPU-hr (B111824), A10 +$0.88 (B111826).

## 2. Storage (per month)

| Item | Part | Price |
|---|---|---|
| Block Volume capacity | B91961 | $0.0255 / GB-mo |
| Block Volume performance units (VPU) | B91962 | $0.0017 / VPU-GB-mo |
| Block Volume, Always Free 200 GB | B91445 | $0 |
| Object Storage standard | B91628 | $0 first 10 GB, then $0.0255 / GB-mo |
| Object Storage requests | B91627 | $0 first 50,000/mo, then $0.0034 per 10,000 |
| Archive Storage | B91633 | $0 first 10 GB, then $0.0026 / GB-mo |
| File Storage (FSS) | B89057 | $0.30 / GB-mo — **~12x block** |
| Logging storage | B92593 | $0 first 10 GB, then $0.05 / GB-mo |

Block Volume defaults to **Balanced = 10 VPU**, so the real price is
`0.0255 + 10 x 0.0017 = $0.0425/GB-mo` — 1.67x the number people quote. Higher Performance
(20 VPU) is $0.0595/GB-mo.

## 3. Egress and networking

| Item | Part | Price |
|---|---|---|
| Egress from **NA / Europe / UK** | B88327 | first 10 TB/mo free, then $0.0085 / GB |
| Egress from **APAC, Japan, South America** | B93455 | first 10 TB/mo free, then $0.025 / GB |
| Egress from **Middle East & Africa** | B93456 | first 10 TB/mo free, then $0.05 / GB |
| Flexible Load Balancer base | B93030 | first **744 LB-hr/mo free**, then $0.0113 / LB-hr |
| Flexible LB bandwidth | B93031 | first 7,440 Mbps-hr/mo free, then $0.0001 / Mbps-hr |
| DNS queries | B88525 | $0.85 / million |
| Email Delivery | B88523 | first 3,000/mo free, then $0.085 / 1,000 |

744 free LB-hours is **exactly one load balancer running all month**. A second one, or the same
one in a second region, bills from its first hour: `$0.0113 x 730 ~ $8.25/mo`. The 10 TB free
egress is per tenancy per month across all regions, not per instance.

## 4. Database (per hour)

| Item | Part | Price |
|---|---|---|
| Autonomous AI Transaction Processing, ECPU | B95702 | $0.336 / ECPU-hr (~$245/mo for 1) |
| Autonomous AI TP, ECPU **BYOL** | B95704 | $0.0807 / ECPU-hr — 4.2x cheaper |
| Autonomous AI Lakehouse (ex-ADW), ECPU | B95701 | $0.336 / ECPU-hr |
| Autonomous AI Database, Developer | B110316 | $0.0391 / instance-hr |
| Autonomous "- Free" SKUs (ATP/ADW/JSON) | B91393, B91391, B93307 | $0 |
| Autonomous AI DB storage | B95754 | $0.0299 / GB-mo |
| Base Database on Ampere A1, Developer | B109635 | $0.022 / OCPU-hr |

2026 naming churn: everything is "**Autonomous AI** Database", ADW is "Autonomous AI
**Lakehouse**", and billing is **ECPU**, not OCPU. Anything quoting "ADW / OCPU" part numbers is
stale.

## 5. Containers and observability

OKE **Enhanced** Cluster B96545 $0.10/cluster-hr (~$73/mo); OKE Virtual Node B96109
$0.015/node-hr; OKE **Basic** Cluster is absent from the price list — its control plane is free,
which is the reason Basic still exists. Monitoring ingestion first 500M points free then
$0.0025/M (B90925), retrieval first 1,000M free then $0.0015/M (B90926); Notifications HTTPS
first 1M free then $0.60/M (B90940), email first 1,000 free then $0.02/1,000 (B90941).
**A Virtual Private Vault is $3.724/vault-hr ~ $2,719/mo** (B90328); the shared default vault is
the free one.

## 6. Two worked stacks

**Always Free maximal** — 4 A1 OCPU (2,920 OCPU-hr vs 3,000 free), 24 GB (17,520 vs 18,000),
200 GB volumes, 10 GB object storage, 1 LB (730 vs 744 LB-hr), 2 Free ADBs, <10 TB egress:
**$0.00**. The bundle sits exactly one unit below every boundary — a 5th A1 OCPU or a 2nd LB
starts billing. On a 744-hour month 4 OCPU is 2,976 OCPU-hr: still under, by 0.8%.

**Typical small PAYG stack** — E5 2 OCPU + 16 GB ($67.16) + 100 GB Balanced block ($4.25) +
50 GB object ($1.02) + 1 LB ($0) + 200 GB US egress ($0) ~ **$72.43/mo**. Quote these deltas
next to it: 2nd LB +$8.25 · 20 VPU boot +$1.70/100 GB · Windows +$134.32 · OKE Enhanced +$73.00 ·
Autonomous AI TP 2 ECPU +$490.56 (BYOL +$117.82) · Virtual Private Vault +$2,718.52 · the same
200 GB egressed from Sao Paulo past 10 TB, ~3x.

Docs (HTTP 200, 2026-09-09): https://www.oracle.com/cloud/price-list/

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| LimitExceeded | Tenancy-wide Oracle service limit hit | id 5 [unverified] |
| TooManyRequests | Per-user/per-tenancy throttle | id 26 [unverified] |
