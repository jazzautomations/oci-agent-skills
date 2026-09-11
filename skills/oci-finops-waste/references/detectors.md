# Detector contracts

Attachment joins include ATTACHING and uncertain non-detached states. AVAILABLE is not
a detach signal. Read every AD before excluding boot attachments. Lists at the bound
become coverage gaps. Current state does not prove how long an instance was stopped.
Multi-attached storage is a stopped-VM candidate only when every joined instance is
known stopped; VPU comparisons require a single attachment for disk attribution.

| ID | Signal | Threshold / evidence | Pricing / limitation |
|---|---|---|---|
| D1 | Detached block volume | No active attachment in scoped complete lists | B91961 capacity + B91962 VPU; cross-compartment attachments need review |
| D2 | Orphan boot volume | Same, across all returned ADs | Same; never derive detach time from creation time |
| D3 | Stopped VM storage | Join stopped instance and attached volume | Storage only; free 200 GB allowance unresolved |
| D4 | Excess VPU | Instance-wide daily P95 DiskIopsRead/Written <25% volume guaranteed, >10 VPU | Delta to 10 VPU × GB × B91962; disk attribution and latency unknown |
| D5 | Idle compute | CPU <5%, memory <10%, network/disk low | Shape SKUs; batch, licensing and month-end review |
| D5-guard | Missing monitoring | Fewer than 90% distinct days covered | Unknown, never idle |
| D6 | Idle LB/NLB | Zero daily traffic and connections | No NLB base charge; LB shared allowance needs usage |
| D7 | Unhealthy LB | Unhealthy daily peaks meet observed backend counts | Align backend sets/timestamps; outage investigation precedes cost action |
| D8 | ADB idle/stopped | State or CPU <10% and sessions <=1 | Free-tier gate; SKU/edition/autoscaling need review |
| D9 | ADB allocation | Used <20% allocated | Units/minimums/SKU unknown; no saving invented |
| D10 | No lifecycle | Exact LifecyclePolicyNotFound code | Missing policy alone never proves cold data |
| D11 | Cold bucket | Zero requests over 30 covered days | Retrieval and minimum retention cost unresolved |
| D12 | Idle NAT | Zero traffic over covered days | No gateway savings claimed |
| D13 | OKE workers | Every active worker daily CPU P95 <10% | Pod requests/limits/memory/HA require Kubernetes access |
| D14 | Backup retention | Manual backup has no expiration | Billed backup SKU and unique bytes require billing evidence; unknown cost |
| D15 | Cost anomaly | Last settled nonzero day > mean+3σ, >=8 days | Original currency; no FX; not full zero-day anomaly analysis |
| D16 | Month forecast | Forecast > explicit scoped budget | --budget-amount and --budget-currency required |
| D17 | Untagged spend | >20% positive scoped spend has no tag | --cost-tag namespace.key required; governance only |
| D18 | Advisor agreement | PENDING resource action, home region | Discard action.url and untrusted price fields |
| W11-parts | Abandoned upload | Multipart age >=7 days | Byte size unknown |
| W12 | Unassigned reserved IP | AVAILABLE without assigned entity | Hygiene, no IPv4 saving invented |
| W13 | Unused capacity reservation | reserved > used | Billing terms and shape unknown |
| W15 | No budget | Complete empty tenancy budget listing | Governance, zero direct savings |
| W18 | VCN without subnets | Complete empty subnet list | Other dependencies unassessed; no network charge |

Utilization uses conservative maxima of **daily P95 buckets**, not a pooled 14-day P95.
Traffic and capacity checks use the stated daily sum, maximum or minimum instead.
At least 90% of distinct days are required; absence, truncation, duplicate series and
wrong identifiers do not count as new coverage. End is exclusive UTC midnight.
Only the region/compartments supplied are assessed. Search corroborates service lists.
The JSON `scope_limitations` and Markdown scope section retain that boundary;
unrequested regions are not a failed check inside the authorized region.
`coverage_gaps` still blocks scoped validation for unreadable/truncated responses,
missing criteria, fewer than eight observed cost days per service/currency, missing
month/currency forecasts or no positive currency-qualified spend for tag analysis.
`complete` remains false: successful scoped checks never certify the entire estate
or establish aggregate savings. Empty billing/forecast data is not a clean finding.
The call budget bounds fan-out and includes retries. 429 retries wait 1 then 2 seconds.
Findings carry review proposals. Where the change is sufficiently specified, the JSON
and Markdown include an inert command template and rollback. Other commands stay null
until ownership, target configuration and dependencies are known. No finding authorizes execution.

Sources reviewed 2026-09-10:
https://docs.oracle.com/en-us/iaas/Content/Block/Concepts/bootvolumes.htm
https://docs.oracle.com/en-us/iaas/Content/Block/Concepts/blockvolumeperformance.htm
https://docs.oracle.com/en-us/iaas/Content/Monitoring/Reference/mql.htm
https://docs.oracle.com/en-us/iaas/Content/Balance/Reference/loadbalancermetrics.htm
https://docs.oracle.com/en-us/iaas/Content/NetworkLoadBalancer/Metrics/metrics.htm
https://docs.oracle.com/en-us/iaas/Content/Block/References/volumemetrics-reference.htm
https://docs.oracle.com/en-us/iaas/Content/CloudAdvisor/Concepts/recommendations-costmanagement.htm
https://www.oracle.com/cloud/price-list/
