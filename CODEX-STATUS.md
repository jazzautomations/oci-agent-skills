# Handoff 8 — complete, merged locally

`v2-foundation` was merged into `main` with `--no-ff` at `eac838d`. All four handoff
items were committed separately before the merge. No push, tenancy mutation, or
history rewrite was performed.

| Item | Commit | Result |
|---|---|---|
| 1 Scoped script sweep | `861a155` | DEFAULT profile, profile region, tenancy-root compartment, first root instance or explicit skip, and the fixed last-hour MQL probe. Data gaps have a distinct status. |
| 2 Empty responses | `18054e5` | Successful blank list/summarize output becomes an empty collection. Monitoring reports `no_datapoints`; malformed responses and service errors remain failures. Collection-consumer regressions cover the shared wrapper, monitoring, certificates, and Audit. |
| 3 History | `daa7d44` | Patch-body scanning exempts Git identities and commit trailers, reports exact blob locations, and suppresses matched values. The owner-operated purge and optional identity rewrite are documented; neither was executed. |
| 4 Release evidence | `0c52607` | Reviewed and committed refreshed evidence on v2-foundation before merging. The report generator uses the actual branch and the script sweep derives its region from the profile. |

## Validation on main

Validation at merge commit `eac838d` passed **295 tests**. Strict package validators,
manifest checks, catalog regeneration, and copied-distribution checks passed without
baseline exemptions. The installed CLI help sweep also passed during this handoff.
The copy contains 33 skills, 15 bundled MCP tools, 16 shared reference files, hooks,
and the portable runtime; research, environments, the authoring stencil, handoff
scratch, and symlinks are excluded.

The refreshed [validation matrix](docs/validation-matrix.md) records **22 PASS and
6 nonpassing gates**. Main validation reuses dated live CLI, MCP, and public-link
evidence; it does not claim those probes were repeated after the merge.

The refreshed [script sweep](docs/validation-scripts.json) invoked all 35 Python/shell
entrypoints: **20 passed, 2 ran with data gaps, 7 failed or returned incomplete
evidence, and 6 stopped for missing prerequisites**. Four SQL examples stayed inert.
Both monitoring entrypoints now record `ran, gap` for the empty fixed MQL probe.
No scope was broadened or resource created to fill missing evidence.

An earlier concurrent test run hit the existing credential-free stdio smoke timeout.
Its isolated rerun and subsequent complete suites passed unchanged. The final suite
retains the existing Authlib deprecation warning.

## Remaining release gates and owners

| Gate | Remaining work | Owner |
|---|---|---|
| V19 FAIL | Description routing proxy is 37.5%, below 90%; no qualifying host-routing result replaces it. | Evaluation/routing maintainers |
| V22 FAIL | One historical audit blob contains two email occurrences, visible in its addition and removal patches. Follow the [exact purge plan](docs/history-purge.md) before the first push. Git identity metadata and commit trailers are exempt. | Repository history owner |
| V24 PARTIAL | Local CLI drift checks passed; hosted Tuesday execution and issue creation remain unmeasured. | Repository CI maintainers |
| V25 FAIL | Resolve the 7 failed/incomplete script results and 6 missing prerequisites; the 2 no-data results remain explicit coverage gaps. | OCI operator / skill maintainers |
| V27 UNAVAILABLE | Installed `plugin eval` remains early-access restricted; no qualifying host task score. | Evaluation maintainers / installed host provider |
| V28 PARTIAL | Four offline arms are complete; the model-backed behavioral comparison remains unmeasured. | Evaluation maintainers |

The merge is complete; the package is **not release-ready**. The existing auth-modes
content and Autonomous Database `.handoff-live.json` user scratch were preserved
byte-for-byte. All package changes are on v2-foundation and included by the merge;
main's final documentation records the post-merge checks.
