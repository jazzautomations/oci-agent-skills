# Routing reliability and task evaluation

The repository's recorded classifier selects the expected skill for 77 of 80
requests in each of two trials. This passes the declared 90% gate, but does not
establish reliable task execution or comparative superiority. Four distinct
requests account for the errors: two fail in both trials and two fail once.
One persistent discrepancy exposes an ownership conflict between the benchmark
and the current skill descriptions. The immediate priority is to resolve those
contracts and measure task outcomes, preserving the existing scores and corpus.

This assessment uses the September 10, 2026 evidence for 37 skill descriptions.
The classifier is `claude-sonnet-5`, with tools and MCP disabled. Public sources
support service boundaries and evaluation methods; conclusions about this
repository are derived from its recorded traces and source contracts. Proposed
methods below have not been deployed or measured here.

## Recorded errors

The [case-level diagnostic](../evals/results/routing-diagnostics.json) decodes
the opaque request IDs from both trials and verifies the underlying evidence
before reporting disagreements. Expected labels include the existing mechanical
skill-merge remap. They have not been changed to accommodate model predictions.

| Case | Request intent | Expected | Seed 17 | Seed 29 | Assessment |
|---|---|---|---|---|---|
| R01 | Find the CLI group after `oci weblogic` fails | `oci-navigator` | `oracle-enterprise-apps` | `oracle-enterprise-apps` | Product name outweighs command-discovery intent |
| R60 | Identify the principal an OCI agent uses for tools | `oci-generative-ai` | `oci-iam-policy` | Expected | Agent architecture is implicit; IAM overlaps |
| R68 | Remove a boot-volume backup policy and explain existing backups | `oci-dr-backup` | `oci-block-file-storage` | `oci-block-file-storage` | Current ownership contract conflicts with the expected label |
| R71 | Determine whether OCI CLI can automate Fusion ERP approvals | `oracle-enterprise-apps` | Expected | No skill | Capability question is treated as an excluded transaction |

R01 is a request to discover a command, not primarily to operate an enterprise
application. The navigator description owns unknown command groups and spelling
errors; enterprise applications excludes CLI spelling discovery. Nevertheless,
both selections follow the WebLogic product name. Oracle documents `wlms` as a
CLI group, which also appears in the repository's pinned catalog. Current online
documentation can describe a newer CLI than the pinned 3.91.0 census, so installed
help remains the appropriate version check.<sup>[1](#source-1)</sup> An enterprise skill may still
give a correct answer: an exact-match selection failure is not proof of an
incorrect task outcome.

R60 needs a distinction between the identity used to call the agent service,
the service identity used for an API-calling tool, and the identity of code
executing a local ADK function. Oracle's API-calling guidance describes a resource
principal with the appropriate IAM authorization. ADK documentation separately
describes host authentication and local function execution.<sup>[2](#source-2)</sup><sup>[3](#source-3)</sup> The request
does not identify that architecture. A task grader should accept a targeted
clarification and reject a confident answer that treats every agent execution
path as the same principal. The current GenAI description could state this
ownership more clearly without claiming that IAM is irrelevant.

R68 is the strongest reason to examine labels before optimizing descriptions.
The DR skill explicitly delegates single-service backup commands to the service
skill; block/file storage explicitly covers boot volumes and backup policies.
Oracle places these concepts under Block Volume, including scheduled backup
expiration and separate manual backups.<sup>[4](#source-4)</sup><sup>[5](#source-5)</sup> Both model selections are
consistent with that contract, although both fail the frozen expected label.
That is evidence of a contract disagreement, not permission to change the gold
label silently. Removing an assignment, deleting a policy, and deleting a backup
also need separate task assertions; this routing result proves none of those
operational semantics.

R71 asks whether an interface supports a workflow. Oracle's `fusion-apps` CLI
group manages Fusion environments; Financials documents separate application
APIs, including retrieval of approval activities.<sup>[6](#source-6)</sup><sup>[7](#source-7)</sup> The existence of that
API does not establish complete approval-flow automation. The appropriate answer
explains the control-plane/application distinction and identifies the required
product and API scope. Excluding actual business transactions from a skill
should not exclude explaining that boundary.

## Measurement and uncertainty

Exactly 76 of 80 routing requests are correct in both trials. The model makes
the same selection for 78 of 80 requests, including the two persistent errors.
Agreement is therefore useful for locating instability but cannot substitute
for correctness. Combining the runs as 154 of 160 would also hide that these
are repeated observations of the same 80 prompts, not 160 independent requests.

The two negative suites each record zero firings across 40 known cases. They
support regression protection on those examples. They do not demonstrate zero
false positives in deployment, especially for unsupported requests close to a
supported domain. CLINC150 made out-of-scope detection an explicit evaluation
problem; later work distinguished difficult in-domain unsupported intents from
obviously unrelated requests.<sup>[8](#source-8)</sup><sup>[9](#source-9)</sup> Appropriate new cases include OCI Classic
comparisons, questions about application APIs, and ambiguous agent identities.

For scale only, a Wilson 95% interval for 77 successes in 80 independent Bernoulli
observations is approximately 89.5%–98.7%. With zero observed failures in 40
independent observations, the exact one-sided 95% upper failure bound is
`1 - 0.05^(1/40)`, approximately 7.2%. These calculations are illustrative:
the maintained, deliberately curated corpus is not an independent sample from
deployment traffic. Neither interval is a calibrated guarantee for this system.

The 80 routing examples have already influenced description repairs. They are
a development regression set, even though labels are hidden during each model
call. An unseen holdout must be collected and frozen separately. Using a test
score to choose descriptions turns that set into validation data; ordinary
leakage guidance applies to prompt and description selection as well as trained
models.<sup>[10](#source-10)</sup> New cases should be grouped by scenario so paraphrases of one
request do not appear on both sides of the split.

The diagnostic now separates three properties: valid evidence, passing gates,
and perfect routing. Tests cover persistent errors, remapped labels, reordered
opaque predictions, stale evidence, and a negative firing despite perfect
positive selection. This makes score interpretation reproducible. It does not
improve model behavior by itself.

## Ownership and adjudication

A skill needs an entry contract that distinguishes the requested action from
the product mentioned. For the disputed cases, useful fields are platform,
service, action, resource, interaction mode, and scope. For example, R01 is
current OCI / WebLogic / discover CLI command / command group / explanation;
R71 is Fusion / ERP / determine interface capability / approvals / explanation.
These are proposed reasoning fields, not an implemented semantic parser.

The contract should specify the first owner and any subsequent delegation.
An entry skill can explain an interface boundary before another skill provides
service details. A single expected label currently compresses that sequence
into one decision. A future task rubric can allow multiple justified paths
while requiring the same factual and operational outcome. That is a different
measurement and must not be retroactively substituted for exact-match accuracy.

For R68, maintainers should decide whether DR owns all backup questions or only
cross-service recovery planning. If DR remains the entry owner, both descriptions
must describe that delegation consistently. If service-local ownership remains
the intended design, record a reviewed benchmark correction in a new corpus
version and report both old and new results. Label-quality research motivates
inspection of suspicious examples, but model disagreement alone does not prove
a label is wrong.<sup>[11](#source-11)</sup>

Adjudication should record the original prompt, applicable contract, expected
answer, accepted routes, reviewer rationale, and corpus version. Historical
traces remain immutable. The present recommendation is to retain 77/80 and the
R68 disagreement until that decision is explicit. Making a description unusually
broad just to capture one known sentence can create new negative firings.

## Mathematical methods and their limits

A parse tree is useful for shell syntax: it can distinguish a command, option,
argument, pipeline, and substitution. It cannot infer whether a request about
Fusion approvals is a capability question or an instruction to perform a
transaction. That requires semantic interpretation and a domain contract.
Similarly, Huffman coding optimizes representation length under a frequency
model; Mersenne primes are number-theoretic objects. Neither supplies the missing
ownership rule. They should not be introduced into routing without a specific,
measurable problem that they actually solve.

| Method | Contribution | Limitation here | Decision |
|---|---|---|---|
| Description classifier | Simple selection over the existing catalog | Sensitive to overlap and wording | Retain as the measured baseline |
| Structured intent fields | Exposes action/product and explain/execute distinctions | Extraction itself can be wrong | Prototype on separate development cases |
| Lexical plus dense retrieval | Finds plausible candidate skills | Product similarity can repeat R01 | Consider only if candidate recall needs it |
| Cross-encoder reranking | Scores the request and candidate jointly | Ranking does not repair contradictory contracts | Compare with the same task budget |
| Conformal prediction sets | Calibrated ambiguity handling under assumptions | Requires scores and separate calibration data | Defer until these prerequisites exist |
| Hierarchical routing | Narrows domain before loading specialist guidance | An early wrong branch can exclude the right skill | Compare against the flat catalog |

Retrieve-and-rerank systems use an inexpensive retrieval stage followed by joint
query/document scoring. Sentence Transformers documents this two-stage pattern
for lexical or dense candidates and cross-encoder reranking.<sup>[12](#source-12)</sup> For 37 skills,
an additional index and model are not automatically justified. First measure
candidate recall, total accuracy, latency and cost. A reranker cannot recover a
correct owner excluded from its candidate set, and a high similarity score does
not authorize an operation.

Conformal prediction provides a more principled way to handle ambiguity than
asking a language model for an unsupported confidence percentage. With a fixed
scoring model `f`, one possible nonconformity score is `s(x,y) = 1 - f_y(x)`.
On a separate calibration set of size `n`, choose the order statistic at
`ceil((n+1)(1-alpha))`, using an infinite cutoff when that rank exceeds `n`.
The prediction set contains labels whose score does not exceed the cutoff.<sup>[13](#source-13)</sup>

Under the applicable exchangeability assumptions, this controls marginal label
coverage. It does not guarantee correctness for each request, each service, or a
changed skill catalog. A singleton, multiple candidates, and an empty set can
support different interaction policies, but an empty set alone is not proof that
a request is out of scope. Research on conformal intent clarification explores
this approach directly.<sup>[14](#source-14)</sup> The current trace stores selected labels rather
than the required candidate scores; there is no basis for attaching a calibrated
95% confidence claim to it.

A suitable experiment would first freeze ownership rules, then fit any scoring
or extraction choices on development data, calibrate on a distinct partition,
and evaluate on a final untouched set. Report prediction-set size, clarification
rate, coverage, false firings, task success and cost together. A system that asks
for clarification on every request can avoid some errors while becoming unusable.

## Task evaluation and the accepted fallback

The outstanding task gate is different from skill triggering. A classifier can
select the right skill while producing an invalid command, choosing the wrong
scope, inventing an API, or ignoring missing prerequisites. Conversely, an
unexpected first skill can delegate and complete the task correctly. Agent
evaluation therefore needs distinct records for the task, repeated trial,
transcript, grader result, and observable outcome.<sup>[15](#source-15)</sup>

The original design allows a skill-creator task evaluation when native plugin
evaluation is unavailable. The recorded native command encountered an
early-access restriction; that explains the native result, not the absence of
the alternative measurement. The imported `evals.json` shape is available, but
having a compatible file is not evidence that the 40 tasks have been executed
and graded.

Inspection of the installed skill-creator implementation also reveals two
different workflows. Its description evaluator observes an early Skill/Read
selection and stops; its broader task workflow runs with-skill and baseline
attempts and grades outputs. Only the latter can address the task gate. The
local description optimization loop chooses descriptions using its reported
test score, so that split functions as validation data, not a final untouched
holdout. This is an inference from the inspected implementation, not a claim
that all versions have the same behavior.<sup>[16](#source-16)</sup>

The alternative should preserve the frozen 40 task prompts and separate their
rubrics from the agent's context. For each task, specify the required artifact
or answer, factual assertions, permitted reads, unavailable prerequisites, and
failure conditions. A command proposal can be graded for shape and explanation
without being executed, but it must be reported as such. Deployment success
requires observed environment outcomes; fixtures cannot establish it.

Run matched with-skill and baseline trials using the same model version,
available tools, sanitized fixtures, time limits, and cost caps. Predetermine
the number of repetitions and retain failed, interrupted and unavailable runs.
Grade deterministic assertions automatically where possible; use blinded human
or model-assisted review for explanation quality, with disagreements recorded.
Do not allow the agent to read the grading keys or other arms' answers.

For the four disputed routing cases, initial outcome assertions should require:
R01 to identify command discovery and consult the installed command surface;
R60 to distinguish the execution architecture or ask a focused clarification;
R68 to distinguish assignment, policy and retained backup behavior without
performing removal; and R71 to explain environment administration versus
application workflows without inventing a general CLI approval command.
These proposed assertions are not completed task results.

Report task success, routing accuracy, negative firing, clarification rate,
unsafe proposals, observed unauthorized actions, latency and cost separately.
A tool-free run structurally cannot mutate a tenancy; that is a harness property,
not evidence that the agent would preserve authorization with broader tools.
Tool design research similarly emphasizes realistic tasks and verifiable
outcomes rather than surface-level tool-call counts.<sup>[17](#source-17)</sup>

## Comparison with Oracle's official skills

The official `oracle/skills` repository is a relevant additional baseline absent
from the archived four-arm comparison. At the inspected revision
`fcbc9430777e8990d6d4382caeb1abdd05b4868d`, its tree contains 14 `SKILL.md`
entrypoints and 977 Markdown files, including 61 under OCI. These are reproducible
tree counts, not counts of equally mature capabilities. Its OCI entrypoint and
authoring guide use domain navigation and progressively loaded specialist
guidance.<sup>[18](#source-18)</sup> Some top-level product areas are placeholders; broad directory
names should not be counted as completed workflows.

That structure offers a useful architectural comparison with this repository's
37 scoped entries, shared references and bounded MCP runtime. It does not show
which system produces better answers. Preserve the historical four-arm table
and its frozen snapshots, then add the Oracle reference prospectively under a
new comparison version. Pin every input revision and model configuration.

Compare shared tasks first and report unsupported coverage explicitly. A skill
that intentionally does not cover a product should not receive a fabricated
task failure without a stated coverage policy. Conversely, a broad coverage
claim needs representative tasks across the claimed domains. Measure factual
outcomes and operational boundaries before using file counts, token counts or
repository size as explanatory secondary metrics. No evidence here supports
calling this repository the best or most complete OCI skill collection.

## Recommended sequence and acceptance criteria

First, keep the new deterministic error report in CI and publish the four-case
audit next to the aggregate score. This step is implemented and requires no new
model calls. A stale diagnostic must fail validation even if an old score passes.

Second, adjudicate ownership for backup questions and specify the agent identity
and capability-question boundaries. Preserve the current corpus and traces.
Any description repair should be evaluated on both the original regression set
and separately authored neighboring negative cases. Repeated collections with
unchanged inputs must not be used to select a favorable result.

Third, implement the accepted task-evaluation fallback with observable rubrics
and matched baseline trials. The target remains the original task threshold of
0.8, with unavailable prerequisites reported separately and no silent removal of
difficult cases from the denominator. This is the missing evidence needed to
move from description selection to claims about agent usefulness.

Fourth, create a new comparison including the pinned Oracle reference, then
evaluate structured intent or hierarchical routing against the same baseline.
Add retrieval or calibrated prediction sets only when the measured failure
pattern justifies their complexity. Reliability research shows why carefully
curated, low-ambiguity evaluations remain necessary even for strong models;
high average accuracy alone does not establish dependable behavior.<sup>[19](#source-19)</sup>

The present assessment supports private technical review with explicit limits.
It supports neither perfect routing nor an end-to-end reliability claim. The
five open release gates remain open; this research resolves the interpretation
of the routing evidence and specifies the measurements still required.

## Sources

All web sources were inspected on September 10, 2026. Local evidence is the
[semantic trace](../evals/results/semantic.json),
[diagnostic](../evals/results/routing-diagnostics.json),
[routing corpus](../evals/routing.json), skill descriptions and
[evaluation guide](evals.md). Private design records are cited by title only and
are not included in the distribution.

<a id="source-1"></a>**1.** Oracle. [WebLogic Management Service CLI reference](https://docs.oracle.com/en-us/iaas/tools/oci-cli/latest/oci_cli_docs/cmdref/wlms.html). Current online CLI documentation; repository census pins 3.91.0.
<a id="source-2"></a>**2.** Oracle. [API Calling Tool Guidelines](https://docs.oracle.com/en-us/iaas/Content/generative-ai-agents/api-calling-tool-guidelines.htm). OCI Generative AI Agents documentation.
<a id="source-3"></a>**3.** Oracle. [Agent Development Kit Quickstart](https://docs.oracle.com/en-us/iaas/Content/generative-ai-agents/adk/api-reference/quickstart.htm). Authentication and local function execution.
<a id="source-4"></a>**4.** Oracle. [Overview of Block Volume Backups](https://docs.oracle.com/en-us/iaas/Content/Block/Concepts/blockvolumebackups.htm). OCI Block Volume documentation.
<a id="source-5"></a>**5.** Oracle. [Scheduling Volume Backups](https://docs.oracle.com/en-us/iaas/Content/Block/Tasks/schedulingvolumebackups.htm). Policy-based expiration and manual backup retention.
<a id="source-6"></a>**6.** Oracle. [Fusion Applications CLI reference](https://docs.oracle.com/en-us/iaas/tools/oci-cli/latest/oci_cli_docs/cmdref/fusion-apps.html). Environment administration.
<a id="source-7"></a>**7.** Oracle. [Workflow Notification Contents / Approval Activities](https://docs.oracle.com/en/cloud/saas/financials/26b/farfa/api-workflow-notification-contents-approval-activities.html). Financials REST API 26B.
<a id="source-8"></a>**8.** Larson et al. [An Evaluation Dataset for Intent Classification and Out-of-Scope Prediction](https://arxiv.org/abs/1909.02027). 2019.
<a id="source-9"></a>**9.** Zhang et al. [Are Pretrained Transformers Robust in Intent Classification? A Missing Ingredient in Evaluation of Out-of-Scope Intent Detection](https://arxiv.org/abs/2106.04564). 2021; revised 2022.
<a id="source-10"></a>**10.** scikit-learn developers. [Common pitfalls: data leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage). Current official documentation.
<a id="source-11"></a>**11.** Northcutt, Athalye and Mueller. [Pervasive Label Errors in Test Sets Destabilize Machine Learning Benchmarks](https://arxiv.org/abs/2103.14749). 2021.
<a id="source-12"></a>**12.** Sentence Transformers. [Retrieve & Re-Rank](https://www.sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html). Official documentation.
<a id="source-13"></a>**13.** Angelopoulos and Bates. [A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification](https://arxiv.org/abs/2107.07511). 2021; revised 2022.
<a id="source-14"></a>**14.** den Hengst, Wolter, Altmeyer and Kaygan. [Conformal Intent Classification and Clarification for Fast and Accurate Intent Recognition](https://arxiv.org/abs/2403.18973). 2024.
<a id="source-15"></a>**15.** Anthropic. [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents). Official engineering article.
<a id="source-16"></a>**16.** Anthropic skill-creator, installed `SKILL.md`, `scripts/run_eval.py` and `scripts/run_loop.py`; local source inspection, September 10, 2026. Original private design record: `00-PLAN-V2.1.md`, sections 3.0 and 6.2. These records document the fallback and are not public task results.
<a id="source-17"></a>**17.** Anthropic. [Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents). September 11, 2025.
<a id="source-18"></a>**18.** Oracle. [oracle/skills at fcbc943](https://github.com/oracle/skills/tree/fcbc9430777e8990d6d4382caeb1abdd05b4868d), [OCI entrypoint](https://github.com/oracle/skills/blob/fcbc9430777e8990d6d4382caeb1abdd05b4868d/oci/SKILL.md), and [authoring guide](https://github.com/oracle/skills/blob/fcbc9430777e8990d6d4382caeb1abdd05b4868d/SKILL_AUTHORING_GUIDE.md). Counts recorded in [reference metadata](evidence/oracle-skills-reference.json).
<a id="source-19"></a>**19.** Vendrow et al. [Do Large Language Model Benchmarks Test Reliability?](https://arxiv.org/abs/2502.03461). 2025.
