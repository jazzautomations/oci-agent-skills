# Well-Architected for OCI — five pillars, and the pages that exist
Source: research/13 §2; every URL verified HTTP 200 on 2026-09-08.

Root: https://docs.oracle.com/en/solutions/oci-best-practices/index.html — *"Learn About the
Well-Architected Framework for Oracle Cloud Infrastructure"*, `dcterms.created` 2025-05-02.

**The framework has five pillars, and performance and cost are one pillar, not two.** Any
answer that lists "cost optimization" separately, or omits Distributed Cloud, is
pre-May-2025.

| Pillar | Focus areas (verbatim from the page) |
|---|---|
| Security and compliance | user authn/authz · resource isolation and access control · database security · data protection · network security · environment monitoring and auditing · optimizing security postures |
| Reliability and resilience | scalability · service limits and quotas · fault-tolerant network architecture · health checks · data backup · data replication · disaster recovery |
| Performance and cost optimization | compute sizing · storage strategy · network monitoring and tuning · cost tracking and management |
| Operational efficiency | deployment strategy · workload monitoring · OS management · operations support |
| Distributed cloud | deployment strategy and workload placement · seamless integration across environments · compliance and sovereignty · resilience and DR · unified operations and optimization |

Distributed cloud is the newest pillar (change log, 2025-05-02) and covers public cloud,
dedicated regions, Cloud@Customer, edge and multicloud. **It is three-fifths unwritten**: it
advertises five focus areas but ships two articles. Citing it beyond deployment strategy and
multicloud database services is inventing.

## The pages, by pillar
Slug prefix `https://docs.oracle.com/en/solutions/oci-best-practices/`; 31 pages walked, not
guessed. Route to the exact page, never the book root.

| Pillar | Pages |
|---|---|
| intro / get started | `index.html` · `simplify-provisioning-oci-landing-zones1.html` |
| Security | `effective-strategies-security-and-compliance1.html` · `manage-identities-and-authorization.html` · `isolate-resources-and-control-access1.html` · `secure-your-databases1.html` · `protect-data-rest1.html` · `ensure-secure-network-access1.html` · `monitor-and-audit-your-environment1.html` · `optimize-security-posture-your-environment1.html` |
| Reliability | `reliable-and-resilient-cloud-topology-practices1.html` · `design-scalability1.html` · `manage-your-service-limits1.html` · `define-your-network-and-connectivity-architecture1.html` · `understand-health-your-workload1.html` · `back-your-data1.html` · `replicate-your-data1.html` · `plan-your-disaster-recovery-strategy.html` |
| Performance / cost | `performance-efficiency-and-cost-optimization-practices.html` · `plan-compute-resources1.html` · `decide-your-storage-solution.html` · `tune-and-monitor-network.html` · `track-and-manage-usage-and-cost1.html` |
| Operations | `best-practices-operating-cloud-deployments-efficiency.html` · `plan-your-deployment-strategy1.html` · `monitor-your-workload1.html` · `manage-your-operating-systems1.html` · `support-your-operations1.html` |
| Distributed cloud | `effective-strategies-distributed-cloud-implementation1.html` · `deploy-multicloud-oci-oracle-database-services1.html` |
| tail | `acknowledgments.html` · `change-log-gvvgq.html` |

The book also defines personas (Application Architect, Cloud Architect, Cloud Operations
Manager, DevOps Architect, …), each mapped to pillars and suggested certifications — a
legitimate way to frame "who is asking" before proposing a design.

## URL traps
- **Do not construct pillar slugs.** `oci-best-practices-networking` (created 2025-10-08) and
  `oci-best-practices-security` resolve; `-reliability`, `-performance`, `-operations` and
  `-distributed-cloud` all 404.
- The **Cloud Adoption Framework** at `https://docs.oracle.com/en-us/iaas/Content/cloud-adoption-framework/`
  is a different book — the governance/organisational layer, including `high-availability.htm`
  and `disaster-recovery.htm`. It is routinely conflated with this one.
- `/en/solutions/` is a reference architecture; `/en/learn/` is a tutorial. Search engines mix
  them; do not cite a `learn` page as a design.
- `dcterms.modified` is not published on these pages — only `created`. Freshness is a floor,
  not a fact. Print the date beside the link so the user can discount it.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| NotAuthorizedOrNotFound | Deliberate ambiguity: missing resource OR missing policy OR wrong region OR wrong compartment | id 13 [unverified] |
| NoEtagMatch | Optimistic-concurrency `if-match` stale | id 23 [unverified] |
