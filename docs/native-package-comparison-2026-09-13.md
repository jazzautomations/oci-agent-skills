# Native package comparison protocol — September 13, 2026

**Status: native preflights passed; Zen/MiMo inference never started. Superseded
by the user-requested [GPT Luna comparison](luna-package-comparison-2026-09-13.md).**
That completed exploratory comparison uses an orchestrator document broker;
it does not fulfill the native protocol below.

The user requested comparison with both Oracle and adibirzu. Automatic approval
review required an explicit confirmation of the private-package payload
and the Zen/MiMo destination after the model-improvement notice. No external
attempt in this three-package experiment has been sent. Earlier interrupted
diagnostics remain separate and will not be pooled into this run.

The corrected installer maps server names directly under `mcp`. Its previous
`mcp.servers` nesting was incompatible with the native OpenCode 1.18.30 schema.
The new regression validates the generated map against that native schema and
rejects the previous shape. Starting the extracted MCP command directly had
missed this host-level failure. See [installation](install.md).

A deterministic local provider exercised native activation and an actual linked
reference read for both packages. OpenCode registered 37 skills from this package
and 27 from adibirzu. Both tests passed with zero external inference and zero OCI
calls; this proves the tested transport path, not model capability. The
[sanitized result](evidence/native-package-preflight-2026-09-13.json) records the
observations. A subsequent [three-package preflight](evidence/native-three-preflight-2026-09-13.json)
passed native activation and a real reference read for each package: 37 registered
skills from this package, 14 registered Oracle entries (including its domain
routers), and 27 from adibirzu. Oracle nested directories were retained. The
local probe recognizes both Markdown links and backtick-delimited reference
paths; its earlier path-discovery failures remain in private logs and are not
model outcomes. The comparison uses canonical `skills/` paths and retains both
`skills/` and `references/` trees. An earlier diagnostic adapter copied host
entrypoints whose rewritten links targeted an omitted canonical tree; those
scores cannot establish a valid reference-enabled comparison.

## Three-package comparison

| Parameter | Value |
| --- | --- |
| Packages | This package; the official `oracle/skills` at `b0afa3bfd7c7e3547458d7fe52649ab1b59706b7`; `adibirzu/oci-skills` at `a4fbf70fd26d1a1c820261a7d4761ebb55457c84` |
| Host/model | OpenCode 1.18.30; `opencode/mimo-v2.5-free` |
| Tasks | Original 40 tasks, each attempted once by each package |
| Order | Task shuffle seed 915; arm-order seed 916; all three arms admitted together in two-task batches |
| Limits | Six concurrent attempts; 16 host steps; 4096 output tokens per request; 240-second response timeout; no structured-output retry |
| Overall bounds | At most 1920 provider requests; stop admitting batches after 45 minutes; the active batch finishes and is retained |
| Payment | No paid fallback or model API payment authorized |
| Evidence | Native transcripts, registered/activated skills, read calls, fixture receipts, original input/source hashes, independent JSON Schema checks |

Oracle and adibirzu are both current opponents. There are 120 task-arm attempts;
the wall-time limit remains 45 minutes. Historical results remain separate. The official
[Oracle Skills repository](https://github.com/oracle/skills) contains domain
entrypoints and nested resources; preserve that layout and verify native
activation and a real linked-reference read before admitting model attempts.
The Oracle MCP repository is a different product and is not treated as an
equivalent skill package.

All three arms receive the same task prompts, output schemas, synthetic observation
server, and inert command-contract tools. The only differing content is the skill
package and its references. Native read permissions cover those document trees;
no shell, generic executor, grader gold-answer directory, or credentialed OCI tool is
available. Original answers and grading criteria remain unchanged. Reads of
references cannot execute their examples.

The primary score is exact fixture-answer correctness with the required
observation reads, valid inert commands, and a successful contract check for each
final command. An incomplete attempt counts as a failure. Report all 40 outcomes
per arm, activation/read counts, completion rate, latency, and model-reported
cost metadata. Such cost metadata is not a provider invoice.

Report paired wins/losses and the exact two-sided binomial test over discordant
pairs for this package against each opponent. Apply Holm correction to these
two comparisons at family-wise alpha 0.05. A higher observed score alone is a descriptive result. A claim of supported
superiority **within this experiment** additionally requires a complete,
source-consistent collection, at least 32/40 successes for this package, and
Holm-adjusted `p < 0.05` against both opponents. Do not rerun failures or change the criteria to obtain that result.

Stop on a source change, insufficient storage, provider refusal, an operator
request, the declared bounds, or three consecutive batches with transport errors.
Keep all attempted outcomes and label an incomplete collection explicitly.

These are author-designed synthetic tasks already used during development, not
a held-out population. The comparison does not test deployment, real account
permissions, mutation workflows, complete query semantics, every competing
repository, or four native products. It cannot establish a universal “best OCI
repository” claim. Historical Claude reference-arm scores (39/40 for this pack,
33/40 for adibirzu, 38/40 for Oracle references, and 38/40 bare) remain evidence
for their original source revision and different protocol.

## External data decision

Running this comparison sends skill/reference text from the private package,
the public Oracle and adibirzu skills packages, synthetic tasks/observations, and the associated
conversation to OpenCode Zen/MiMo Free. No OCI credentials or real account data
are included. [Zen's privacy terms](https://opencode.ai/docs/zen/#privacy) permit
model-improvement use of MiMo free-tier content. This disclosure needs explicit
authorization before inference. Installer validation is complete. The executable
collector admits no model attempts before the local three-package preflight passes.
