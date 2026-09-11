# Second validation lab — September 11, 2026

This follow-up extends the [first lab](live-validation-2026-09-11.md); it does not
erase failed measurements or claim universal correctness. Standard repository
validation remains read-only. Provisioning, loading synthetic data and audit
configuration were separate owner-authorized operations in a new disposable ADB,
within the owner's aggregate USD 20 allowance. No existing application DB was used.

## Retrieval: measured improvement and cost in latency

The [fixture](../evals/rag-relevance-2026-09-11.json) contains the original five
questions and ten author-written regressions, frozen before the second lab's
initial outcomes. Each question was executed three times, sequentially, with no
excluded warmup. Hit@5 means that an expected source appears among five returned
results, not that an answer is correct. The corpus has 15 public repository files.

| Method | Chunks | Expected-source hits | Pooled median latency |
|---|---:|---:|---:|
| Original 300-word vector chunks | 185 | 39/45 | 145.064 ms |
| 100-word vector chunks | 632 | 42/45 | 147.700 ms |
| 100-word exact per-document vector ranking | 632 | 42/45 | 156.127 ms |
| Hybrid document ranking | 632 | 42/45 | 298.064 ms |
| Published document fusion, RRF k=60 | 632 | 45/45 | 1,690.767 ms |

Evidence: [baseline](evidence/rag-relevance-baseline-2026-09-11.json),
[two shorter-chunk variants](evidence/rag-relevance-candidates-2026-09-11.json),
[hybrid](evidence/rag-relevance-hybrid-2026-09-11.json),
[final published implementation](evidence/rag-relevance-fusion-2026-09-11.json).

Baseline misses: redaction-original and credential-publication. Shorter chunks
fixed those but missed error-404; hybrid still missed redaction-original. Fusion
was developed **after** these failures, combines fixed top-five rankings with equal
reciprocal-rank weights, and does not read expected labels. Its 15/15 question
result is a development result, not independent held-out validation. The final
source-hashed implementation was measured again, rather than substituting the
experimental helper's output. Individual samples, including the slow first call,
are retained; no throughput, concurrency, tail-latency or scalability claim follows.

Default `query.py` now uses fusion; vector/hybrid modes remain explicit options.
The fusion vector leg is exact per-document ranking, not proof that the optimizer
used HNSW. Both named indexes were VALID. Re-executing the published loader kept
15 unique documents and 632 chunks, then explicit hybrid-index synchronization
and the redaction query succeeded. [Reload evidence](evidence/rag-reload-2026-09-11.json).

The [embedding model](https://huggingface.co/sentence-transformers/all-MiniLM-L12-v2)
truncates long inputs at 256 wordpieces. The 100-word setting is a practical shorter
chunk heuristic, not a guarantee of a tokenizer-token ceiling. Oracle documents
the [hybrid row identifier/source mapping](https://docs.oracle.com/en/database/oracle/oracle-database/26/vecse/query-hybrid-vector-indexes-end-end-example.html).

## SQLcl: database audit without agent write grants

The published `setup.py --audit` applies `audit.sql` as ADMIN, before the agent
connects. It enables policy RAG_DEMO_ACCESS for SELECT and INSERT on RAGAPP.DOC_TAB
by RAGMCP, with explicit rollback. No audit, DDL or DML privileges are granted to
RAGMCP. Its session privilege list remained exactly CREATE SESSION, with READ on
the two demo tables. [Identity checks](evidence/rag-audit-2026-09-11.json).

Actual SQLcl 26.2.2 MCP, restriction level 4, used an isolated saved RAGMCP
connection; ADMIN was not saved there. A marked SELECT succeeded. A marked
zero-row synthetic INSERT was denied with ORA-41900. Both appeared in the database
unified audit trail with SQLcl client attribution and RAG_DEMO_ACCESS.
[Sanitized receipts](evidence/sqlcl-unified-audit-2026-09-11.json).

The denied INSERT's MCP envelope had `isError=false`; SQL result content must also
be inspected. Oracle audit recorded return code 2004, not the client code 41900.
Duplicate audit rows are not counted as distinct requests. This establishes those
specific audited operations, not complete public/inherited privilege review,
all-operation logging, retention or tamper-resistance certification. It does not
create SQLcl's absent DBTOOLS$MCP_LOG table. See [Oracle unified auditing](https://docs.oracle.com/en-us/iaas/autonomous-database-serverless/doc/adb-audit.html).

## Four-arm task measurement

The [controlled tool benchmark](tool-task-benchmark.md) attempted all 40 original
prompts in each of four arms, with real calls to one isolated synthetic MCP reader.
Strict scores were pack 39/40, adibirzu references 33/40, Oracle tool references
38/40 and bare 38/40. Six attempts exhausted the fixed per-attempt budget; all
failures remain in the denominator. It cost a reported USD 3.3107418 for the final
collection. Offline verification checks inputs, actual read receipts and grades.
This is reference-assisted task interpretation, not native plugin deployment or
evidence of statistical superiority. The report preserves failed preflight runs.

## Account restrictions and persistent configuration

A categorical, tenancy-scoped subscription read returned ACTIVE, Universal Credits,
PaaS and IaaS. This confirms an active subscription, not Support eligibility or a
particular remaining credit balance. No account identifiers or subscription values
are included in public evidence.

A separate Cloud Guard activation attempt allowed more than two minutes after
creating the documented 22-statement service policy. Correctly formed requests
then returned HTTP 500 InternalServerError twice. Configuration reads still showed
DISABLED. The newly created policy was removed; no targets or responders were
created. The earlier immediate 404 attempt remains in its own report. These
statuses do not prove a Free Tier restriction or a specific authorization cause.
Support user validation remains HTTP 403 AUTHZ_FAILED.

The setup did not upgrade the account, install automatic responders or change
application resources. Credentials remain in private local configuration, not in
Git. Database auditing applied only to the disposable lab. Persistent repo changes
are code, tests, documentation and sanitized evidence; default query behavior
changes to fusion and the loader changes to shorter chunks as described above.

## Cleanup, budget and verification

The second ADB reached TERMINATED at 17:39:42 UTC, with zero backups in a complete
bounded response. Its cleanup fallback timer was stopped only after that result.
[Teardown receipt](evidence/second-lab-cleanup-2026-09-11.json). Independent bounded
reads at 17:43 UTC found zero active ADBs in the selected root scope, confirmed the
new Cloud Guard policy absent and protection still DISABLED. Same-day posted cost
rows were still empty: this is billing delay, not proof of zero charges.
[Account/cleanup verification](evidence/second-lab-account-2026-09-11.json).

The final task benchmark reported USD 3.3107418. Two aborted collections reported
USD 0.9617534 combined; two isolated tool preflights reported USD 0.0207576; the
earlier answer pilot reported USD 0.25907. Recorded model calls therefore sum to
**USD 4.5523228**. Cancelled in-flight calls may have additional unreported usage;
these CLI values are not a reconciled provider invoice. The first lab's less-than-
one-hour compute estimate was USD 0.706; the second lab used less than half an hour
at USD 0.672/hour, thus less than USD 0.336 compute before storage and tax. Planning
remained below the USD 20 ceiling; final invoiced spend and credits remain unverified.
All paid lab compute has been terminated in the verified scope; no paid evaluation
process remains running.

The full explicit regression command passed **479 tests**, with one dependency
deprecation warning. The fixture-evidence verifier validates the recorded attempts
offline; it intentionally retains `complete=false` because six model attempts did
not complete. Neither a green evidence verifier nor a green unit suite changes
the service- and provider-dependent gates below.

The final [release recheck](evidence/second-lab-release-gate-2026-09-11.json) ended
with 23 PASS and exactly five nonpassing gates: V22, V24, V25, V27 and V28. CLI
fence validation checked the installed help surface, not cloud mutations. Additional
[strict checks](evidence/second-lab-extra-checks-2026-09-11.json) passed, and the
[public-source freshness recheck](evidence/second-lab-freshness-2026-09-11.json)
found no changes or unavailable sources. Changes remain in the local checkout;
no commit, remote push or history replacement was performed in this follow-up.

## Remaining release gates

The [matrix](validation-matrix.md) remains the authority. V22 still includes a
published-history finding; a separately cleaned candidate is ready for owner
review, but no force-push was authorized. V24 still lacks the actual Tuesday cron
and real notification outcome. V25 retains Cloud Guard/Support failures and FinOps
coverage limitations; settled cost history cannot be manufactured in a new account.
Native V27 is provider-restricted. The separate controlled four-arm tool benchmark
does not instantiate all native reference products and therefore does not silently
replace the original V27/V28 acceptance criteria.
