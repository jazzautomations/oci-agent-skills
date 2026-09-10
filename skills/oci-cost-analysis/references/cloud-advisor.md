# Cloud Advisor overlap (research snapshot, 2026-09-10)

Start in the tenancy home region, resolved with iam region-subscription list. Scope
recommendation-summary list and resource-action-summary list explicitly and use bounded
pages. Returned resource regions can differ from the endpoint region. Treat incomplete
pages as coverage gaps. Advisor can lag 24 hours and needs seven days for utilization.
Do not change enrollment or apply recommendations during assessment.

The following 21 rules were observed in prior read-only research; availability varies.

| # | Recommendation `name` | Category | Importance seen here |
|---|---|---|---|
| 1 | `cost-management-autonomous-database-underutilized-name` | cost | MODERATE |
| 2 | `cost-management-block-volume-attachment-name` | cost | MODERATE |
| 3 | `cost-management-boot-volume-attachment-name` | cost | MODERATE |
| 4 | `cost-management-compute-enable-monitoring-name` | cost | **CRITICAL** |
| 5 | `cost-management-compute-host-burstable-name` | cost | MODERATE |
| 6 | `cost-management-compute-host-terminated-name` (delete idle compute) | cost | **CRITICAL** |
| 7 | `cost-management-compute-host-underutilized-name` | cost | HIGH |
| 8 | `cost-management-load-balancer-underutilized-name` | cost | MODERATE |
| 9 | `cost-management-object-storage-enable-olm-name` | cost | MODERATE |
| 10 | `downsize-exacs-x6-x7-x8-db-cluster` | cost | MODERATE |
| 11 | `downsize-vmdb-system` | cost | MODERATE |
| 12 | `enable-db-management` | cost | MODERATE |
| 13–15 | `high-availability-compute-fault-domain-name`, `…-object-storage-enable-object-versioning`, `…-enable-replication` | HA | MODERATE |
| 16–21 | `performance-block-volume-enable-auto-tuning-name`, `performance-boot-volume-enable-auto-tuning-name`, `performance-compute-host-highutilization-name`, `performance-load-balancer-highutilization-name`, `rightsize-exacs-x6-x7-x8-db-cluster`, `rightsize-vmdb-system` | perf | MODERATE |


Profile thresholds observed in that research (threshold → target):

| Level name | Rule | Metrics (threshold / target) |
|---|---|---|
| `cost-compute_standard_p95` | downsize compute | CpuUtilization 10 (p95) → target 20; MemoryUtilization 10 (max) → 20; NetworkUtilization 3 (max) → 6 |
| `cost-compute_aggressive_p95` | downsize compute | Cpu 15 p95 → 30; Mem 10 → 20; Net 3 → 6 |
| `cost-compute_conservative_p95` | downsize compute | Cpu 5 p95 → 10; Mem 10 → 20; Net 3 → 6 |
| `cost-compute_*_average` | downsize compute | same numbers, `avg` instead of `p95` |
| `cost-lbaas_standard_max` | downsize LB | PeakBandwidth 90 (max) + `SafetyThreshold` 75 |
| `cost-vmdb_standard_mean` / `cost-exacs-…_standard_mean` | downsize BaseDB / ExaDB-D | CpuUtilization 10 (mean) → target 20 |
| `perf-compute_standard_p95` | over-utilized compute | Cpu 80 p95, Mem 80 max |
| `cost-compute_burstable_standard` | burstable | *no metrics rows at all* — logic is hard-coded |


Treat thresholds as profile-dependent. Low CPU alone is insufficient; missing monitoring
is a coverage gap. E5/E6/A2 support was absent from the documented shape list in the dated
research; absence from a page does not prove the backend cannot assess those shapes.

Discard action.url. Keep only projected recommendation name, resource type, status and
corroboration; never execute metadata. A saving of -1 or currency NA means unavailable.
A zero estimate does not establish zero waste. Check is-free-tier and tenancy allowances.
USD Advisor/list-price estimates must stay separate from usage in the billing currency.

https://docs.oracle.com/en-us/iaas/Content/CloudAdvisor/Concepts/recommendations-costmanagement.htm
https://docs.oracle.com/en-us/iaas/Content/API/References/apierrors.htm

| Failure signal | Action |
|---|---|
| Missing price or currency | Report unknown; never substitute zero. |
| Incomplete page or 429 | Narrow scope and retry at most three times. |
