# Native-host follow-up — September 11, 2026

This follow-up establishes native plugin loading and a distributed MCP price
lookup, then measures 40 paired synthetic tasks. It does **not** make the
repository 100% release-validated. V22/V24/V25/V27/V28 retain their nonpassing
status; the [matrix](validation-matrix.md) separates these gates.

## Native installation and price path

A fresh copy installation contained no symlinks before runtime startup. Claude
2.1.268 loaded plugin `oci-agent-skills` 0.2.1 and discovered its 37 namespaced
skills. A first isolated probe successfully activated `oci-cli-auth`, read the
synthetic identity fixture, and returned its exact expected answer: $0.0603638,
4,297 ms. This was not a live OCI identity check.

The next probe activated `oci-agent-skills:oci-cost-analysis` and called the
distributed `mcp__oci-readonly__oci_price_lookup` with B95702/USD. Its numeric
answer matched the tool response: 0.336 USD per ECPU-hour. The response identifies
the public Oracle catalog and snapshot `2026-09-09T16:34:38.537Z`. The tool performs
a public HTTP GET; that snapshot is the provider's last-update field, not the
request time. This proves the installed tool path, not an account-specific price.
Fifteen bounded MCP tools were discovered, but only price lookup was called.
Cost was $0.0902886; duration 6,921 ms. [Projected transcript](evidence/native-public-price-2026-09-11.json).

Both probes used an absent OCI configuration, an isolated working directory,
restricted host mode, explicit MCP configuration and no Bash/Read tools. No OCI
account mutation or credential retrieval occurred. Host-managed skill names can
still appear in discovery; they were not called in the qualified probes.

## Paired task measurement

[Collector](../scripts/eval/native_task_benchmark.py),
[original results](../evals/results/native-task-benchmark-2026-09-11.json), and
[post-collection syntax audit](../evals/results/native-command-audit-2026-09-11.json).

The original 40 prompts are unchanged. Each arm ran once per task, in a fresh
session, using `claude-sonnet-5`, low effort, order seed 83 and a requested
$0.10 per-attempt cap. Eighty attempts cost **$2.9407216**. Failures were retained
without retries. Both arms used the same structured answer schema, synthetic
MCP observations and instruction to propose inert, bounded read commands.

| Measurement | Native plugin | No plugin |
|---|---:|---:|
| Collected attempts | 40 | 40 |
| Responses accepted by collection protocol | 39 | 40 |
| Confirmed namespaced native skill activations | 28 | 0 |
| Original answer + receipt + command-shape score | 33/40 | 28/40 |
| Same records after stricter syntax adjudication | 32/40 | 16/40 |

The original command grader mistakenly accepted `--all` together with `--limit`
and rejected quoted logical OR inside JMESPath. The separate audit applies the
same corrections to both arms, also checking pinned CLI aliases, literal enum
choices through OCI's case-insensitive conversion and JMESPath parsing.
Fifteen grades changed: 14 passes became failures
and one failure became a pass. Neither the original scores nor responses were
overwritten. CI recomputes both artifacts without model calls.

T26 in the native arm returned a successful host response but invoked the
unqualified name `oci-cost-analysis`. The collector required the plugin namespace,
rejected the attempt and retained its calls/cost. This is a protocol rejection,
**not** a budget exhaustion or demonstrated host execution failure. No credit
was added retrospectively. T39's read proposal also failed the destructive-task
output contract; it did not execute a mutation.

These are deliberately limited measurements:

- The fixture universe is synthetic, not the user's live tenancy.
- Skill invocation is native, but file access is disabled: following referenced
  documents/scripts is unmeasured. Activation was requested explicitly, not a
  natural-trigger benchmark.
- Proposed commands are never executed. Syntax does not establish query meaning,
  service callback requirements, completeness of inventories or workload success.
- Mutation tools are absent; review-only answers do not certify runtime defense
  against a hostile tool or an authorized write-capable host.
- One run per arm/task on development cases is not a holdout or significance test.
- Native competitor deployments were not measured. This cannot replace V28.
- `claude plugin eval` remains early-access-restricted. The available experiment
  does not establish all original alternative-evaluation criteria for V27.

Recheck the recorded evidence without spending money:

```bash
uv run --frozen --project runtime python scripts/eval/verify_native_task_benchmark.py evals/results/native-task-benchmark-2026-09-11.json
```

Use a Python environment containing pinned `oci-cli==3.91.0` for the independent
command audit; it imports metadata but executes no proposed command:

```bash
python scripts/eval/verify_native_command_audit.py evals/results/native-task-benchmark-2026-09-11.json evals/results/native-command-audit-2026-09-11.json
```

## Support triage repair

The incident sweep omitted the OCI user context and projected a nonexistent
`data.items` wrapper. It now supplies `--ocid` from `USER_ID`, projects the actual
array, and accepts `OCI_HOME_REGION` / `OCI_IDENTITY_DOMAIN_ID` when applicable.
Missing user context fails closed before a service call. Unit tests cover missing
context, forwarded headers, list counts and a persistent 403.

A [real bounded call through the repaired helper](evidence/native-support-recheck-2026-09-11.json),
with explicit user and home region, still returned HTTP 403. Verified email and an active user did not resolve
Support access. The helper reports access denied without guessing entitlement;
registration, Support privileges and domain context still require verification.
See Oracle's [user setup](https://docs.oracle.com/en-us/iaas/Content/GSG/support/validate-user.htm)
and [Support prerequisites](https://docs.oracle.com/en-us/iaas/Content/GSG/Tasks/usingsupport.htm).
No ticket, IAM policy or registration change was made in this follow-up.

## Cost and remaining release conditions

The [full strict recheck](evidence/native-release-gate-2026-09-11.json) passed
**496 tests** in 109.55 seconds, with three dependency deprecation warnings and no
test failures. After adding the enum-conversion regression, the
[final full-suite rerun](evidence/native-final-regression-2026-09-11.json) passed
**497 tests** in 53.10 seconds, with the same three warnings.
Overall release status remains 23/28 PASS. The separate
[post-edit checks](evidence/native-extra-checks-2026-09-11.json) passed all eight
checks, including verification of both task benchmarks. The pinned-CLI audit was
also independently recomputed and matched. Actual CLI help was not rerun in this
follow-up; the previous live-help evidence remains dated and linked in the matrix.

Known model charges across this ongoing session now total **$7.6436968**:
previously recorded $4.5523228 plus $0.0603638 + $0.0902886 + $2.9407216.
Earlier disposable OCI compute estimates remain below about $1.05, before storage,
taxes and final billing. Posted spend is delayed; this is not a reconciled invoice,
and uncaptured canceled calls may exist. The user's **$20 aggregate ceiling was
not renewed**. No new paid OCI resources were created here; both earlier labs
remain documented as deleted.

Still needed for the original release claim: approved published-history cleanup;
actual scheduled drift/notification evidence; Cloud Guard and Support access plus
owner-defined FinOps criteria/settled data; qualifying complete host task
evaluation; and the original native four-product comparison. A clean offline
suite or the restricted native experiment cannot substitute for these conditions.
