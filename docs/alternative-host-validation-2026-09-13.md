# Alternative host follow-up — September 13, 2026

The installed Devin CLI and OpenCode were exercised after the previous Claude
runner could not complete authentication. These are separate host/model
experiments. They do not replace the four-product comparison, live service
coverage or full task semantics. Each experiment used the then-current task prompts, expected answers and
command grader. Subsequent repairs are recorded separately. The [sanitized evidence](evidence/alternative-host-attempts-2026-09-13.json)
records the partial attempts, source revision, score replay and local checks.

## Devin

Devin CLI 3000.10.21 authenticated with the existing Free plan. The available
`swe-1-6-slow` model accepted calls; models requiring a paid plan were not used.
A fresh copy contained all 37 skills, with bounded synthetic observation,
reference-document and inert command-contract tools. Native skill bodies were
observed. File execution, cloud execution and unrelated tools were denied.

The initial phase attempted 19 task/arm pairs: eight with skills and eleven
without. The original strict JSON parser accepted and passed two with skills and
four without. The other attempts retain their original failures. Six native
responses used a Markdown envelope: removing only that envelope in a separately
labelled diagnostic would recover five; the sixth still contains an invalid,
unchecked command. This diagnostic does not rewrite the original scores.

The continuation attempted only previously unattempted pairs, first checking the
existing Free plan before each call. Of five further baseline attempts, one
passed, two reached scope/call limits, and two were refused after the weekly
allowance was exhausted. Across both phases, 24 of the planned 80 pairs were
attempted; seven passed the original strict collection/grading protocol. This
partial, unbalanced sample cannot estimate a skill improvement or close V27/V28.

No upgrade or credit purchase was made. Token list-price calculations in the
private research logs are estimates, not charged or reconciled billing. The
[Devin pricing page](https://devin.ai/pricing) describes Free-plan included usage
separately from paid plans and purchased extra usage.

## Separately authorized account setup

An additional Cloud Guard setup request selected Oracle-managed resources
(`self_manage_resources=false`). This account setup was separate from read-only
repository validation. Configuration read before and after the request remained
`DISABLED`; the update returned HTTP 404. The agent created no policies, targets
or responders and requested no paid features. The response does not distinguish
an entitlement issue from other authorization or resource causes, and the reads
do not establish the absence of every possible service-internal side effect.

Support access, settled cost history and the other live coverage requirements
remain unresolved. Repeating local tests cannot manufacture those prerequisites.

## OpenCode access and remaining validation

OpenCode 1.18.30 reached the existing owner-operated local model through a
private gateway. The isolated installation registered all 37 skills; preflight
observed a native skill body, an allowed shared-reference read and a denied
out-of-scope read. Only the fixed synthetic observation and inert command checker
were exposed, along with native document/skill access. Both fixed MCP servers
advertised no resources or resource templates. No generated OCI command ran.

The model is Nemotron 3.5 Lightning 30B-A3B Q4_0 behind the local `jazz-coder`
alias. This uses existing Compute capacity; no model API plan, new instance or
credit purchase was created. Existing Compute billing continues independently.
The later local-model collector checkpointed four rows: three native attempts
(one pass, two failures) and one baseline failure. One native failure proposed an
invalid command without invoking a skill; another loaded a skill but returned
an invalid, unchecked query. The passing native row loaded a skill and satisfied
the original grader. A fifth in-flight archive has no recorded final score.
The collector session was unavailable when work resumed; its termination cause
is not established. The separately declared nine-native-failure stop was never
reached. All partial rows and original scores remain preserved. This is not a
completed paired measurement or evidence of an improvement rate.

The fresh local suite passed **589 tests, three warnings, in 46.91 seconds**.
All **28 strict CI validator commands** passed, including full CLI-help lint and
replay of historical evidence. The failed temporary mixed-suite attempt remains
in the private logs; the original complete suite was rerun successfully.

V24 still needs the actual Tuesday scheduled event. V25 still needs live service
access and data. V27 needs a qualifying current task measurement; V28 needs the
original native-product comparison. None of these criteria was waived.

## OpenCode Zen and subsequent repairs

A separate native OpenCode run used `opencode/mimo-v2.5-free`. Its checkpoint
contains **27 of 80 pairs**: nine native attempts (seven completed, five original
passes) and eighteen baseline attempts (ten completed, seven passes). The collector
terminated with `ENOSPC` while copying an installed skill tree. The original
report, failure log and hashes are preserved; its input/score replay passed before
source changes. This partial, unbalanced sample cannot establish an improvement.

No model API payment or paid fallback was used. The [Zen documentation](https://opencode.ai/docs/zen/)
marks this model free and permits model-improvement use of its content. Only
package documents and synthetic fixtures were supplied; no generated OCI command
executed. The free offering may change.

The [repair follow-up](skill-repairs-2026-09-13.md) records corrections motivated
by this run and independent review. In particular, one original false negative
compared `20.0` with `20` by serialized digest. Its separately labelled numeric
readjudication does not overwrite the historical report or constitute a new trial.
