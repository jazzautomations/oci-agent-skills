Purpose: the six clocks that delete, stop or downgrade things in a free OCI account, and the
read that tells them apart from a limit. Source: research/04b §16-17, research/06c §1, §6.
Verified 2026-09-09 on CLI 3.91.0, us-chicago-1.

## Contents
The clocks · Idle reclamation · The ADB auto-stop · Trial end · Diagnosing "Oracle deleted it"

## The clocks
| Clock | Window | What happens | Survives? |
|---|---|---|---|
| Free trial credits | 30 days or $300 | Trial ends; the account stays active | Always Free does |
| Post-trial grace | 30 days | Paid resources are reclaimed unless upgraded | Always Free does |
| A1 overhang | 30 days after trial end | A1 above 2 OCPU / 12 GB is disabled, then deleted | No |
| Idle compute | 7 days | Always Free instance may be reclaimed | No |
| Idle Autonomous DB | 7 days | Stopped, not deleted; restart by hand | Data does |
| Account inactivity | 60 days | Free account marked inactive | Reactivation needed |

Two of these are routinely conflated: the promotion's 30-day grace protects **paid** resources,
while the 60-day inactivity clock is about the account itself.

## Idle reclamation
Oracle may reclaim an Always Free compute instance when, over a **7-day window, all** of these
hold together: CPU 95th percentile below 20%, network below 20%, and — A1 shapes only — memory
below 20%. Paid instances are never subject to it. The rule is written policy, not folklore,
which is why "Oracle deleted my instance" is usually this.

Read daily CPU samples as diagnostic evidence:

```bash
oci monitoring metric-data summarize-metrics-data --compartment-id "$TENANCY_ID" \
  --namespace oci_computeagent --query-text 'CpuUtilization[1d].percentile(0.95)' \
  --start-time "$START_TIME" --end-time "$END_TIME" \
  --query 'data[].{r:dimensions.resourceId,p:"aggregated-datapoints"}'
```

`[verified]` this call ran clean and returned **zero datapoints** on the reference tenancy,
whose only instance is `STOPPED`. That is the trap: an empty result is not evidence of idleness
and not evidence of safety. No datapoints means no Compute agent reporting — a stopped
instance, a missing or disabled agent plugin, or a metric outside the window. Say which of
those it is before drawing a conclusion, and never report "safe from reclamation" from an empty
series. This returns daily percentiles, not a single percentile over seven days.
Memory and network need separate queries (`MemoryUtilization`, `NetworksBytesIn`);
the policy is an AND, so a single dimension proves nothing either way.

Retain backups and review the current reclamation terms for Always Free resources.
A PAYG account can still use Always Free resources; upgrading alone is not evidence
that a particular instance is exempt from reclamation.

## The ADB auto-stop
An Always Free Autonomous Database stops itself after 7 days without connections or CPU. The
data is preserved and the database restarts by hand; repeated cycles are what people report as
"Oracle deleted my database". Detect it, do not recreate it:

```bash
oci db autonomous-database list --compartment-id "$TENANCY_ID" --limit 20 \
  --query 'data[?"is-free-tier"].{n:"display-name",st:"lifecycle-state",cpu:"cpu-core-count"}'
```

`[verified]` on the reference tenancy this returns one `is-free-tier` database in `STOPPED`
with `cpu-core-count` 0. Recreating it would spend one of the two `adb-free-count` slots and
lose the data that was never gone.

## Trial end
- The account stays active. Always Free resources keep running with no interruption.
- Paid resources provisioned with trial credits are reclaimed unless the account is upgraded.
- **A1 overhang:** if total A1 exceeds 2 OCPUs / 12 GB when the trial ends, all A1 instances
  are disabled and deleted after 30 days. Get under the allotment *before* the trial expires.
- **Object Storage:** during the trial you may store more than 20 GB, but if you are over 20 GB
  when it ends, **all objects are deleted**. Check `storage-bytes` against actual usage first.
- Home region is chosen at signup and cannot be changed; Always Free compute and Autonomous
  Databases exist only there.
- Upgrading to PAYG keeps every allotment at $0 and keeps all resources. It is asynchronous and
  fallible — stalls of over a week are documented `[unverified]` — so never gate a plan on the
  upgrade having completed. Confirm by re-reading the limits, not by assuming.

## Diagnosing "Oracle deleted it"
Order the checks: (1) is the resource merely `STOPPED`, (2) does a limit read show the
allotment intact, (3) does `resource-availability get` show usage that still counts it, (4) was
there a trial-end or reclamation window in between. Audit events are the only record of an
actual deletion and belong to oci-logging-audit; do not assert a deletion without one.

Docs: https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm
· https://docs.oracle.com/iaas/Content/GSG/Tasks/signingup_topic-What_Happens_When_the_Promotion_Expires.htm
· https://docs.oracle.com/en-us/iaas/Content/Billing/Tasks/changingpaymentmethod.htm
