# MQL cookbook
Source: research/09b §§2–3.
These query expressions are [unverified] service examples until the chosen namespace emits the named metric. Use a bounded start/end window and confirm units and dimensions. Thresholds are illustrative, not an SLO.
| Intent | MQL |
|---|---|
| Mean CPU | CpuUtilization[1m].mean() |
| High CPU | CpuUtilization[1m].mean() > 80 |
| Memory pressure | MemoryUtilization[5m].mean() > 90 |
| Peak CPU | CpuUtilization[5m].max() |
| Request count | AllRequests[5m].sum() |
| Object errors | Errors[5m].sum() > 0 |
| LB unhealthy backend | UnHealthyBackendServers[1m].max() > 0 |
| DB storage pressure | StorageUtilization[5m].mean() > 85 |
| Per-resource CPU | CpuUtilization[5m].groupBy(resourceId).mean() |
| Missing CPU series | CpuUtilization[1m].absent() |
Interval, query range and resolution serve different purposes. A percentile, rate or sum must match the metric's units and sampling semantics. Filter values are untrusted labels; validate them and construct query text deliberately, never evaluate returned text.
Missing-series alarms need a known expected series and a tested absence window. A zero-row query is not a successful threshold test. validate_mql.sh refuses to proceed with zero datapoints and never creates an alarm, even when datapoints exist.
