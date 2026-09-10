# OCI waste assessment

Region: us-chicago-1. Read calls: 56. Bounded sample; absence is not proven.
List-price exposure is not confirmed savings. Shared allowances and overlapping findings are not summed.

| Pattern | Resource | Evidence | USD monthly exposure |
|---|---|---|---:|
| D3 | sha256:3a2ee745b733 | Storage attached to a currently stopped instance; stop duration unknown, compute excluded | 1.9975 |
| D8 | sha256:ecd47f1d31b1 | ADB stopped; compute excluded; storage and free-tier eligibility require billing check | unknown |
| D10 | sha256:64dca4329738 | No lifecycle policy; storage access and minimum retention need review; bytes=571250 | unknown |
| W15 | sha256:9ef77c0e97ec | No budget in a complete bounded tenancy list | unknown |
| D18 | sha256:3a2ee745b733 | Cloud Advisor pending: performance-boot-volume-enable-auto-tuning-name | unknown |
| D18 | sha256:66bd91c1ca05 | Cloud Advisor pending: cost-management-object-storage-enable-olm-name | unknown |

## Coverage gaps

- insufficient metric coverage: AllRequests sha256:64dca4329738
- regional scope only: other regions require separate explicit scans
- unreadable: usage-api usage-summary request-summarized-usages
- D16 forecast needs explicit scoped budget amount and currency
- D17 untagged spend needs --cost-tag namespace.key

Evidence: executed read-only 2026-09-10 in one explicitly selected compartment and region,
56 bounded CLI reads. Resource identifiers hashed; names omitted. STOPPED VM storage,
free-tier stopped ADB, no lifecycle policy and missing budget observed. Two Advisor
recommendations corroborated. No resource changed. Exposure is not confirmed savings.
Only these paths have live non-empty evidence; other detectors have fixture/shape evidence.
The settled usage read failed and cold-bucket metric coverage was insufficient, as listed.
