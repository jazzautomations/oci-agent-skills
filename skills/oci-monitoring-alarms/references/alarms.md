# Alarm review
Source: research/09b §§3–4.
An alarm compartment and metric compartment can differ; specify both. Validate namespace, query, region, dimensions and time window before creating a disabled proposal. validate_mql.sh requires explicit times spanning at most 24 hours and reports only series/datapoint counts.
Any zero-data, query error or malformed response blocks the helper. Nonzero data means the query is reviewable, not that the threshold, notification or SLO is correct. Review missing data behavior, pending duration, severity, repeat interval, suppression and destination delivery separately.
An enabled alarm can send messages and trigger automation. No alarm creation, enablement or notification publication is executed here. Test delivery only after explicit authorization. Preserve the previous query/enabled state and destination list for updates; delete only a newly created test alarm for rollback.
For noisy alarms, inspect aggregation/window/labels first. Suppression is a change that can hide an incident; use a bounded maintenance window with an owner.
