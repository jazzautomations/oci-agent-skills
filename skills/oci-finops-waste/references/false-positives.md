# Review before claiming savings

| Signal | Pitfall | Required check |
|---|---|---|
| STOPPED | Weekend/batch/DR host | Owner and stop timestamp; creation time is not stop time |
| AVAILABLE volume | Healthy attached volumes are AVAILABLE too | Attachment lists, all ADs; ATTACHING is claimed |
| Price exposure | Shared free allowance may cover the whole volume | Billing evidence and tenancy-wide eligibility |
| Free ADB | Stopped and zero CPU is normal | is-free-tier; confirmed savings is zero |
| Low CPU | Memory, I/O, licensing, burst or HA constraint | All relevant metrics and workload schedule |
| Missing metrics | Agent off or wrong dimension/namespace | Coverage gap, not idle |
| No bucket policy | Small/hot/retained bucket | Access, retrieval charges, retention minimum |
| Manual backups | Compliance or rollback point | Owner retention policy; never auto-delete |
| Empty listing | Auth failure or page bound | Report unreadable/truncated scope distinctly |
| Duplicate findings | D1/D4 or D8/D9 overlap | Do not sum exposure across alternative actions |
| Advisor saving -1 / NA | Estimate unavailable | Never sum; ignore action.url |

Public reports use stable hashed IDs and exclude display names. Dynamic identifiers are
retained only in memory for scoped read joins. No secret values, customer objects or database
rows are fetched. Actions are review proposals, not executable deletion automation.

Source: https://docs.oracle.com/en-us/iaas/Content/CloudAdvisor/Concepts/recommendations-costmanagement.htm
