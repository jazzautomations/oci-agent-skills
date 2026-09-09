# Handoff 9 — complete on main

All three items were completed in order, with one commit per item on `main`.
No push, tenancy mutation, new credentialed tenancy read, or history rewrite was
performed. Research remains build-only and is excluded from the distribution.

| Item | Commit | Result |
|---|---|---|
| 1 Guard paths | `bc316be` | Recognizes root and skill script paths, directly or after `bash`/`python3`, including plugin-root variables, absolute paths and root-relative forms. Script and registry SHA pins remain required; missing or changed scripts require review. |
| 2 Severity wording | `df4be4b` | README, foundation docs and the V8 report generator describe the shared generator and sha-pinned severity snapshot. The independent assertion is zero allows outside the strict read-only set. |
| 3 Cleanup and evidence | This commit | Removed `skills/oracle-autonomous-db/.handoff-live.json`, added `skills/*/.handoff-*` to `.gitignore`, applied reviewed release-gate diffs and recorded this status. |

## Validation

The full suite passed **354 tests** before each item commit; item 3's suite is
recorded as V14 in the [validation matrix](docs/validation-matrix.md). The existing
Authlib deprecation warning remains. Guard coverage includes 60 combinations of
script directory, extension, root prefix and interpreter, with unknown paths,
changed script hashes and changed registry hashes requiring review. The fixtures
are inspected as text and never executed.

Strict package validators passed without baseline exemptions: frontmatter,
portability, references, fences, tracked-file secret scanning, budgets, licenses,
read-only script policy, template, manifests, both host strict validations,
script/example and CLI catalog regeneration, offline examples, routing negatives
and copied-distribution inspection. The installed CLI help sweep passed for item 1;
later items used strict snapshot fence validation with unchanged command shapes.
Catalog script/example artifacts were regenerated after script changes.

The copy installer produced a portable tree containing 33 skills, scripts, shared
references and runtime together. Research, environments, the authoring stencil,
handoff scratch and `CODEX-STATUS.md` are excluded; the fresh tree has no symlinks.
The copied guard also passed direct inspection of the new invocation forms without
executing the scripts. Existing auth-modes content was preserved unchanged.

## Release evidence and remaining owners

`uv run --frozen --project runtime python scripts/ci/release_gate.py` ran in its
default diff mode, writing evidence outside the checkout. The reviewed matrix,
offline-example timestamp and host-probe provenance were copied into the tree.
Its exit code was **1**, as expected with **22 PASS and 6 nonpassing gates**.
Live CLI, script, MCP and public-link evidence was reused with its recorded dates;
those probes were not repeated for this handoff.

| Gate | Remaining work | Owner |
|---|---|---|
| V19 FAIL | Description routing proxy remains 37.5%, below 90%; no qualifying host-routing result replaces it. | Evaluation/routing maintainers |
| V22 FAIL | Historical patch bodies still contain the previously identified email occurrences. Follow the [history purge plan](docs/history-purge.md) before the first push; the current tracked-file scan passes. | Repository history owner |
| V24 PARTIAL | Local CLI drift checks pass; hosted Tuesday execution and issue creation remain unmeasured. | Repository CI maintainers |
| V25 FAIL | Archived script evidence still has 7 failed/incomplete results and 6 missing prerequisites; 2 no-data results remain explicit coverage gaps. | OCI operator / skill maintainers |
| V27 UNAVAILABLE | Installed `plugin eval` remains early-access restricted; no qualifying host task score. | Evaluation maintainers / installed host provider |
| V28 PARTIAL | Four offline arms are complete; the model-backed behavioral comparison remains unmeasured. | Evaluation maintainers |

Handoff 9 is complete. The package remains **not release-ready** for the reasons
above; no baseline exemptions or scope expansion were used to change those gates.
