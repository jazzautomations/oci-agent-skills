# Offline follow-up — September 11, 2026

This follow-up makes no fresh model calls, OCI calls, deployments or IAM changes.
It does not turn CI success into full release certification. V24/V25/V27/V28
remain open, with their existing criteria and owners.

[Local checks](evidence/offline-followup-checks-2026-09-11.json) passed **577 tests**
with three warnings in 104.74 seconds, plus the full leaf-only CLI-help check.
All strict offline subchecks passed; the [raw release matrix](evidence/offline-followup-release-gate-2026-09-11.json)
retains 24 PASS, two PARTIAL, one FAIL and one UNMEASURED. Its nonzero exit reflects
those four existing gaps. The raw V27 command text retains the historical probe's
provenance; `evidence_mode=recorded` confirms it was not invoked in this follow-up.

## Repairs and evidence boundaries

Security posture now distinguishes literal names in a structured findings list
from narrative explanations. A name-only schema must not receive names with
appended statements or rationales. It also explains that an any-user-only request
must exclude policies matching only the broader administrator predicate.
The `skill-creator` review kept this a narrow body change, without changing the
description, adding benchmark answers or weakening a grader.

A deterministic regression exercises the authored policy projection on synthetic
records, specialized to the requested condition. It checks exact names and rejects
extra narrative, nonfindings, missing observations and missing final-command checks.
This is a component test, not a fresh model answer: **T04 remains a recorded FAIL**.
The frozen proposal grader also rejects `||` anywhere, including inside a quoted
JMESPath expression; the newer command contract accepts that valid query syntax.
That historical grading limitation is unchanged. The focused any-user test narrows
the actual authored predicate instead of relaxing the grader or regrading reports.
The generic skill validator still rejects the pre-existing `compatibility` field;
the repository's format and size validators support it, so the field is retained.

The earlier 4/5 native versus 3/5 baseline regression is now historical as well.
Its exact report and original offline verifier are pinned to `eafde85` in the
historical-evidence allowlist. The older five reports retain their `0cd2730` pin.
Only these two fixed local revisions and fixed verifier entrypoints are accepted;
no network fetch, report-selected executable or history rewrite is involved.
Changing a report prevents historical replay. A five-case report cannot pass the
full forty-case verifier. Original reports, prompts, fixtures and grades are intact.

The default release gate previously tried `claude plugin eval`, which had returned
an early-access restriction. It now reuses dated access evidence without starting
inference. A missing or malformed report becomes UNMEASURED; it never triggers a
paid fallback. Only the explicit `--probe-host` option can request that probe,
and its help identifies the separate model-provider budget approval requirement.
Tests intercept subprocess launches and verify this default behavior.

## Cost clarification

Claude Code evaluation sessions reported model identifier `claude-sonnet-5`.
Those evaluation costs are **not OCI infrastructure usage or OCI credits**.
The recorded cumulative model cost is $15.12589, including $0.5024286 for the
last ten-attempt regression. These are host-reported cost values, not a reconciled
provider invoice or proof of an additional payment. No account billing mode or
subscription treatment was verified.

Earlier OCI compute was separately estimated below approximately $1.05; storage,
taxes, uncaptured canceled sessions and final invoice reconciliation remain unknown.
Do not treat their sum as a settled charge or the difference from $20 as confirmed
spendable credit. The original aggregate ceiling has not been renewed. Fresh
model inference is paused; continuing repository work does not itself approve a
new model-provider allocation. This follow-up adds zero reported inference cost
and creates no paid OCI resources.

## Remaining external and behavioral work

- V24: the September 11 GitHub API recheck returned no runs for the weekly drift
  workflow with `event=schedule`. Manual publication and deduplication remain
  recorded separately; they do not substitute for the actual scheduled trigger.
- V25: Cloud Guard, Support and FinOps retain the dated service/prerequisite gaps.
  No new service probes or account changes were made in this follow-up.
- V27: current full forty-task behavior and the T04 repair need new behavioral
  evidence. Replaying earlier outputs cannot demonstrate improved model behavior.
- V28: the native four-product comparison remains unmeasured. The normalized
  synthetic comparison is preserved but is not a substitute.

See the [validation matrix](validation-matrix.md) for the complete gate state.
