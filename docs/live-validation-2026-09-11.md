# Live validation and MCP timing — September 11, 2026

This run uses a newly configured API-key profile in `us-chicago-1`. It does not
inherit deployed-workload evidence from the previous account. The initial scope
had no instances, networks, buckets or child compartments.

## Verified results

Latest: [second-lab results](second-validation-2026-09-11.md) add a separate paid
ADB, final RAG fusion measurements, SQLcl unified auditing and the controlled
four-arm tool-task benchmark. The following paragraphs describe the first lab
and its immediate follow-up; their counts and limitations are historical.

Follow-up: the full local suite now passes **468 tests**. The
[account checks and rollback](release-readiness.md#further-validation-and-rollback-september-11),
[paired fixture-answer pilot](task-answer-pilot.md) and
[SQLcl local-log inspection](evidence/sqlcl-local-log-2026-09-11.json) add evidence
without replacing the earlier dated integration measurements below. The model
pilot reported US$0.25907; no additional paid OCI infrastructure was created.

- Local suite after the integration fixes: **460 passed**, one dependency deprecation
  warning. Scope: `tests` and the incident-triage, security-posture and SDK tests.
- CLI examples: **36 successful bounded reads**, **232 syntax-only examples**.
  Syntax-only examples were not executed against OCI.
- MCP: 15 tools discovered; invalid compartment input rejected. The selected
  11 live calls passed in all three benchmark runs: **33/33**. This represents
  10 distinct tools because VCNs and subnets use two variants of one tool.

The sweep previously supplied daily dates to a monthly cost comparison, omitted
required pricing and FinOps arguments, and invoked migration scripts without
their synthetic inventory. It now uses two settled calendar months, explicit
bounded FinOps scope, and an isolated synthetic migration pipeline. FinOps
coverage gaps remain gaps even when its process exits successfully.

## Timing method

Run from the repository root with a configured `DEFAULT` profile:

```bash
uv run --frozen --project runtime python scripts/eval/benchmark_mcp.py --live --region us-chicago-1 --runs 3 --report /tmp/oci-mcp-benchmark.json
```

The [raw measurements](evidence/mcp-benchmark-2026-09-11.json) contain every sample,
dependency versions, source revision, dirty-source indicator, counts, truncation
and startup times. Each run starts a fresh stdio process. Calls are sequential,
with no excluded warmup. Later calls can reuse authentication initialized by
earlier calls. Other validation processes were running on the same host, so these
are observed validation-session timings, not an isolated performance baseline.

| Call | Successes | Median ms | Min–max ms |
|---|---:|---:|---:|
| Identity | 3/3 | 1346.837 | 1053.646–1354.181 |
| Public price | 3/3 | 687.971 | 589.222–2104.753 |
| Regions | 3/3 | 484.437 | 460.272–487.289 |
| Compartments | 3/3 | 465.241 | 448.857–466.762 |
| VCNs | 3/3 | 1049.487 | 815.650–1138.666 |
| Subnets | 3/3 | 527.697 | 458.877–553.287 |
| Buckets | 3/3 | 785.422 | 746.555–847.477 |
| Resource search | 3/3 | 571.335 | 549.607–653.450 |
| Limit services | 3/3 | 469.269 | 460.828–480.875 |
| Limit values | 3/3 | 511.401 | 503.814–524.567 |
| Cost summary | 3/3 | 581.098 | 575.188–644.066 |

These are end-to-end client timings, including stdio, authentication, setup and
service latency. Three samples do not support a p95, throughput or load claim.
Successful empty reads establish API access, not workload behavior. Truncated
resource-search and limits responses are bounded samples, not complete inventories.
No comparison with a competing agent or model task-completion score is implied.

## Paid integration scope

The operator authorized a **US$20 ceiling** for this session, including temporary
resources and cleanup. The separate 26ai laboratory uses two ECPUs, 20 GB storage,
no compute autoscaling and a single-egress IPv4 ACL. Its planned lifetime is at
most two hours, with a host timer to initiate cleanup. Current public list prices
retrieved on September 11 are US$0.336/ECPU-hour (B95702) and
US$0.1953/GB-month (B95706). Two hours of compute are approximately US$1.344,
before storage, backups and taxes. This is an estimate, not posted billing.

## Infrastructure results

The [paid-lab sweep](evidence/paid-lab-scripts-2026-09-11.json) records 38 passed
entrypoints, two failed triage entrypoints, two FinOps coverage gaps and four inert
SQL examples. No entrypoint remains blocked by an absent infrastructure fixture.
Passed entrypoints include both local/synthetic checks and live reads; the report
labels their execution mode. The sweep makes no resource mutations.

Temporary fixtures comprised a VCN, egress gateway, subnet with no inbound security
rules, E5 Flex VM (1 OCPU, 2 GB memory, 50 GB boot volume), private empty bucket,
Functions application, DevOps project and notification topic without subscriptions,
plus a Bastion and a metadata-only forwarding session. No function, pipeline or
SSH forwarding connection was executed. VM agent metrics had real datapoints.

Both triage wrappers completed eight of ten steps successfully. Cloud Guard problem
listing returned 404 and Support listing returned 403. These are failed reads,
not empty results; credits alone did not resolve them. The cause is not established
from the HTTP status. FinOps retains missing billing/tag/resource-coverage evidence
and does not assert complete coverage or total savings.

## Database and retrieval results

The dedicated paid ADB reported API version `26ai` and database engine version
`23.26.3.2.0`. TLS with server identity verification worked. The Oracle-published
MiniLM model was retrieved successfully (133,322,334 bytes). Loading the public
corpus produced **15 documents, 185 chunks, 384-dimensional embeddings**.
`DOC_CHUNKS_HNSW` and `REFS_HYBRID_IDX` both reported `VALID`.

The [RAG benchmark](evidence/rag-benchmark-2026-09-11.json) records 30/30 successful
retrieval calls, five questions, two modes, three repetitions. The vector mode
included the expected candidate source in **4/5 questions**, consistently across
repetitions. The redaction question returned catalog/PowerShell chunks instead of
`references/redaction.md`; this miss is retained, not relabeled. Approximate/exact
top-five displayed-chunk overlap was 1.0 in this tiny corpus; this does not establish
index usage or large-corpus recall. Hybrid queries returned five results, but hybrid
relevance was not manually graded.

| Question | Vector median ms | Hybrid median ms | Vector expected source in top five |
|---|---:|---:|---|
| Redaction | 836.666 | 303.411 | No |
| Untrusted values | 831.999 | 298.077 | Yes |
| Authentication | 831.312 | 296.604 | Yes |
| Regions/realms | 831.476 | 296.604 | Yes |
| PowerShell | 841.006 | 299.212 | Yes |

These existing demo questions form a development set. Query order is fixed, exact
queries warm embedding inference, and the same connection is reused. Corpus hashes,
implementation hashes and every sample are retained. No held-out accuracy, p95,
throughput, superior retrieval quality or competing-agent performance is claimed.

The [SQLcl evidence](evidence/sqlcl-mcp-2026-09-11.json) records version
**26.2.2.233.1901**, Java 21, and nine MCP tools through stdio with restrict
level 4. Only the dedicated `ragmcp` connection was saved in an isolated Java user
home. Connection discovery, connection, document-count SELECT and grant inspection
succeeded. MCP protocol negotiation selected the server-supported version.

The [privilege checks](evidence/rag-privileges-2026-09-11.json) found only CREATE
SESSION plus READ on the two demo tables. A zero-row INSERT and a locking SELECT
were both refused with ORA-41900. DBTOOLS$MCP_LOG was absent; durable SQLcl audit
logging and a comprehensive inherited/public privilege review remain unverified.

Reloading the corpus a second time committed successfully and preserved exactly
15 documents and 185 chunks. This validates the no-duplicate-growth path on this
corpus; it does not establish all interruption/recovery scenarios.

## Cleanup and cost

At 16:50 UTC, [independent cleanup checks](evidence/cleanup-2026-09-11.json) confirmed
the ADB `TERMINATED`, zero database backups, zero active instances, zero boot
volumes across all subscribed availability domains, and zero VCNs, subnets,
buckets, Functions applications, DevOps projects, notification topics and Bastions
in the selected root scope. The cleanup fallback timer was then deactivated.

The paid database and VM ran for less than one hour. At the retrieved list rates,
one full hour of their compute is US$0.706 (ADB US$0.672 plus E5 US$0.030/OCPU and
2 GB × US$0.002/GB-hour), before storage, other service charges, discounts and tax.
This is a conservative compute-only estimate, not an invoice or a total-cost claim.
The US$20 ceiling was used for planning; posted usage charges remain unverified
because billing data is delayed. No active lab resource remains accumulating
compute charges in the verified scope.

Other release gates remain governed by the [validation matrix](validation-matrix.md).
