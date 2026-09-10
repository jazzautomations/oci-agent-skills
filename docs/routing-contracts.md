# Routing ownership contracts

The first skill owns the decision the user is asking for. A product name alone
does not determine that owner. The selected skill may delegate service details;
selection never grants permission to perform a change.

## Decision and delegation

| Requested decision | First owner | Delegation |
|---|---|---|
| Find a missing or rejected current OCI CLI command/group | `oci-navigator` | Service owner after the installed command surface is resolved |
| Choose Oracle Database / Base Database / Exadata resource families | `oracle-db-fleet` | The selected database service owner; generic navigator is excluded |
| Explain whether an Oracle application action is reachable through OCI CLI | `oracle-enterprise-apps` | Product-specific application API; execution remains outside this skill |
| Identify who executes an OCI AI agent's tools and signs downstream requests | `oci-generative-ai` | `oci-iam-policy` after identifying managed versus host execution and the principal |
| Write a policy for an already identified principal | `oci-iam-policy` | Service documentation for exact resource families and permissions |
| Assess the effect of backup-policy changes on retention or recoverability | `oci-dr-backup` | Service skill for scoped command shapes and inventory |
| Obtain a service-local backup command or inventory without a recovery assessment | Service skill, such as `oci-block-file-storage` | DR only if retention/recovery impact becomes a question |
| Assess quota headroom versus physical capacity without free/trial context | `oci-support-limits` | Compute after the capacity assessment |
| Explain explicitly requested Free Tier eligibility or trial lifecycle | `oci-free-tier` | Support/limits for the separate capacity question |

Capability explanation and executing the operation are distinct requests. A
question about whether Fusion approvals are supported is eligible for an
interface explanation; a request to approve an invoice is outside this pack's
enterprise-app execution scope. An unresolved agent architecture calls for a
focused clarification within the GenAI workflow, not invented IAM statements.

## Backup ownership decision

The earlier contract excluded every single-service backup command from DR while
the frozen R68 request expected DR for a combined removal-and-retention question.
The revised contract distinguishes an impact assessment from command mechanics,
regardless of how many services are mentioned. This is an explicit responsibility
change, not a correction to Oracle's service taxonomy: Block Volume still owns
the underlying API.

R68 therefore starts with DR because it asks what happens to existing backups,
then delegates the command to storage. A command-only removal request goes
directly to storage. Both directions are included in the new synthetic cases.
Policies, assignments, and completed backups must remain separate concepts; a
schedule change does not establish unlimited retention or successful recovery.

The original 80 prompts, 40 negatives, expected labels, merge remap, model, trial
seeds and passing thresholds are unchanged. The earlier 77/80 evidence is
preserved in [the pre-change trace](../evals/results/semantic-before-ownership.json).
The earlier 15 synthetic cases remain intact; sixteen additional cases test adjacent
requests, delegation and excluded execution. These are development regressions,
not an unseen holdout.

## Validation protocol

Collect both predefined main trials and the complete 31-case boundary suite
once for this contract version. Keep any failures; do not repeat unchanged inputs
until a preferred score appears. The existing budgets remain USD 0.75 per main
trial and USD 0.25 for the boundary collection. Model sessions have no tools,
MCP servers or OCI config. Recorded inputs and predictions are verified in CI.

An initial candidate exceeded the 400-character description limit. Its collection
was interrupted before a trial result was recorded; the final candidate passed
metadata validation before collection. No completed unfavorable trial was omitted.

The first completed ownership repair scored 79/80 in both main trials, with zero
negative firings and 25/25 boundaries. R01 still failed in seed 17; seed 29 instead
selected Free Tier for R13's generic A1 capacity question. Its
[traces](../evals/results/semantic-ownership-development.json),
[boundaries](../evals/results/semantic-boundaries-ownership-development.json) and
[description inputs](../evals/results/ownership-development-inputs.json) are
preserved. The next candidate explicitly assigns CLI name errors to navigator
and requires free/trial context for Free Tier, adding four counterexamples.
An A1/ARM shape alone does not establish a free account. This is a changed-input
experiment, not an unchanged-input reroll.

The second candidate scored 80/80 and 79/80, but failed the negative gate on N40
(editing an Integration flow in the visual designer). R49 also went to navigator
instead of database-family discovery. Its
[rejected traces](../evals/results/semantic-name-scope-development.json),
[29-case boundaries](../evals/results/semantic-boundaries-name-scope-development.json)
and [inputs](../evals/results/name-scope-development-inputs.json) are retained.
The final descriptions explicitly exclude database-family selection from
navigator and visual Integration-flow editing from enterprise applications.
Two added boundary cases exercise those exclusions. The 80/80 trial alone was
not accepted as evidence that this candidate passed.

The [evaluation guide](evals.md) reports the collected outcome. The
[research report](routing-reliability.md) remains the historical diagnosis that
motivated these changes. Description selection measures entry ownership only;
the 40-task outcome evaluation and matched baseline comparison remain separate
work. A routing repair does not close those gates.
