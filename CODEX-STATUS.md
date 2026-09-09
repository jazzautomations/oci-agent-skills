# Handoff 7 — completed, release not ready

Branch: `v2-foundation`. Seven groups completed as separate commits; no merge to `main`, provisioning, IAM changes or tenancy mutations.

| Group | Commit | Result |
|---|---|---|
| 1 Guard | `97152db` | Monotonic severity, host-permission passthrough, shell-token fix, independent severity matrix and inert parser regressions. 245 tests passed. |
| 2 Sanitizer | `a2f327e` | Preserved line separators, corrected flag, novel-string detection and benign-name fixes. 247 tests passed. |
| 3 Scripts | `88e1780` | Certificate cap 20, saturation reporting, actual wrapper-call checks and scoped script sweep. 254 tests passed. |
| 4 Content | `0facdee` | Diagnostic evidence, route discriminators, exact scope variables, query/bounds lint, shared command-card routes, six grant removals and deletion of 22 skill handoff notes. 256 tests passed. |
| 5 Installation | `dc8db6e` | Bundled MCP declaration, target-runtime setup instructions, handoff exclusion and profile-region fallback. 257 tests passed. |
| 6 Claims | `a320700` | Frozen corpus and explicit scorer remaps, history scan, scratch/diff release runner and measured host framing. 260 tests passed. |
| 7 Release | This commit | Reviewed full matrix, refreshed evidence and final documentation review; final status at repo root only. |

Every implementation commit passed pytest and strict content validators without baseline exemptions. The frozen-corpus prerequisite was pulled into group 1 so its commit could be green. Final review tightened route wording and preserved explicit SQL unverified labels.

## Final evidence

The full `scripts/ci/release_gate.py --live --links --live-help` run used code commit `a320700` and wrote to an external scratch directory. Its diffs were reviewed and secret-scanned before adoption. The [matrix](docs/validation-matrix.md) records **22 PASS / 6 nonpassing**, including **260 passing tests**, installed-help validation, catalog regeneration, 149 expected public URL statuses, 35 successful selected CLI reads and 12 successful MCP live checks. The [host probe](docs/plugin-host-discovery.json) independently discovered all 15 bundled tools through `claude --plugin-dir` without invoking an OCI tool.

All 35 Python/shell skill entrypoints were invoked: 20 passed, 9 failed or returned incomplete evidence, and 6 stopped for missing prerequisites. Four SQL examples remained inert. Results and owners are in [script evidence](docs/validation-scripts.json); no failure was reclassified as an empty success.

## Nonpassing gates and owners

| Gate | Remaining work | Owner |
|---|---|---|
| V19 FAIL | Description proxy is 37.5%, below 90%; the 78/80 saved judge result is description-only and does not establish host routing. Original judge run identifiers remain unavailable and attribution is explicitly unverified. | Evaluation/routing maintainers |
| V22 FAIL | Historical email addresses remain in reachable Git metadata/patches. Real-length OCID and key-block scans found no matches. History was not rewritten. | Repository history owner |
| V24 PARTIAL | Local CLI drift check passed; hosted Tuesday execution/issue creation was not exercised. | Repository CI maintainers |
| V25 FAIL | Resolve missing resource prerequisites and investigate failed/incomplete scoped script reads; see per-entry results. No resources were created or scope broadened to fill gaps. | OCI operator / skill maintainers |
| V27 UNAVAILABLE | Claude Code 2.1.266 still returns “`plugin eval` is currently in early access”; no qualifying host task score. | Evaluation maintainers / installed host provider |
| V28 PARTIAL | Four offline arms are complete; model-backed behavioral scores and no-plugin task deltas remain unmeasured. | Evaluation maintainers |

The raw source/schema estimate is 6,386 tokens. Measured skills-only host framing adds 5,517 tokens; adding the 3,455 schema estimate gives 8,972 as a mixed estimate, not an observed MCP-on total. [Method and measurements](docs/context-measurement.json).

The copy installer was inspected before runtime setup: no research, environments, authoring stencil, handoff notes or symlinks shipped. The target runtime was then initialized and its stdio smoke passed. The existing auth-modes content and Autonomous Database `.handoff-live.json` user scratch were preserved.
