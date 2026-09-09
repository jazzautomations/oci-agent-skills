# Audit, provenance and limits

Reviewed 2026-09-09. This pack's content and CLI shapes are checked independently; a research citation does not establish successful runtime behavior. Research and upstream checkouts are build-only. Sanitized upstream measurements and licensed evaluation snapshots ship where needed to reproduce published comparisons.

## Provenance matrix

| Source | Material used | Shipped implementation/evidence |
|---|---|---|
| Plan v2.1 and errata; research 04a–04d, 06–16 | Skill ownership, scope, command pitfalls, auth, references, catalog and Windows gaps | 33 SKILL.md files and shared/skill-specific references; plan stencil retained as SKILL.md.template |
| research 05 and guard-hook-regex-v2 | CLI census labels, parser risks, denylist counter-evidence | guard_rules.json, guard classifier/replay tests, catalog snapshots; historical denylist artifact in docs/denylist-coverage-research.json |
| research 15 | Untrusted-output contract and ten carrier classes | shared sanitizer, skill hard rules, evals/safety.json; no live injection claim |
| research 17 and data/eval-corpus.json | Unedited routing/negative/task prompts with source URLs | evals/routing.json, negatives.json, tasks.json, both task shapes and explicit remaps |
| adibirzu/oci-skills at a4fbf70fd26d1a1c820261a7d4761ebb55457c84 | Scoped workflow, CLI-help verification, domain breadth; comparison inputs | Independently authored skills; evaluation snapshot b.json, MIT notice and prompt-hook token count |
| oracle/mcp at e3cdae7fad817173ef62882f4d04b6baa32f0be2 | Auth library, typed tools and API discovery; comparison inputs | Locked oracle-mcp-common dependency; API/Cloud descriptions and denylist snapshot with UPL notice |
| research/data/oracle-mcp-smoke.json | Recovered upstream initialize/tools-list and operational-read evidence | docs/oracle-mcp-research.json, preserved rather than inferred from a lost session |
| marcocanto/oci-support-request-skill at be4dcf27eafea066e2ba95924aee2ebd1b808864 | Fixed argv, bounded inspection, scope projection and conditional changes | Support/limits skill and shared read wrappers; idea reuse, no blanket feature parity |
| araidon/oci-skills; cvranjith/arch-diagram-skill | Diagram/spec and architecture review ideas | Architecture routing references; diagram tooling stays outside the runtime |
| oci-ai-architects/claude-code-oci-ai-architect-skills | AI/architecture topic discovery | Research leads checked against installed command shapes |
| Oreo-Tech/oci-mcp | Task inventory and compartment scoping | Fixed read adapter; mixed write surface not imported |
| jasonwilbur/oci-pricing-mcp | Pricing workflow and caching ideas | Fixed public Price List request; no pricing server vendored |

Snapshots are data for offline grading, never executed plugin instructions. Refresh comparison snapshots with `uv run --frozen --project runtime python scripts/eval/head_to_head.py --refresh-snapshots`. Runtime dependencies retain their own licenses; LICENSE/NOTICE and evals/arms/LICENSE-* preserve project and snapshot attribution.

## Measured surface

`uv run --frozen --project runtime python scripts/release_report.py` reproduces skill/example counts, the guard matrix, token estimates, unowned service counts and both denylist comparisons. CLI regeneration is `python scripts/inventory.py --format jsonl --index --check` using Python with OCI CLI 3.91.0 installed. Script/fragment regeneration is `python scripts/inventory.py --scripts --examples`; repeated outputs are byte-identical.

The installed census has 174 groups and 9,145 leaves including aliases. These are installed syntax facts, not complete cloud product coverage. Artifacts retain scope disclaimers: “including aliases”, “no safety or authorization classification”, and “conditional requirements may exist in callbacks”, plus per-module import_errors and validation_levels. Census labels are heuristic inputs to measured guard tests, never an IAM authorization model.

The current OCI-only guard matrix is read 3,697/11/0; mutating 0/3,781/0; destructive 1/997/328; unknown 2/328/0 (allow/ask/deny). All 278 CRITICAL leaves are denied. The single destructive-labelled allowance is an estimate operation mislabelled by the census. This is the actual stricter matrix, not the older 2/996 plan split. Non-OCI rules remain unmeasured hand rules.

The source historical Oracle audit reports 2,222 denylist entries, 374 destructive and 2,644 mutating leaves allowed, 135 reads denied. Current prefix replay gives 374, 2,511 and zero respectively. Both are retained with their distinct classification/matching basis; no current-server claim is derived from historical counts. A generic executor's denied-command list is not a read-only boundary.

≈6.3–6.5k tokens (≈3,020 descriptions + ≈3,300–3,500 MCP schemas, estimates).

This is the prescribed planning estimate. Current shipped descriptions are 11,722 characters, approximately 2,931 tokens; serialized MCP schemas add approximately 3,455, total 6,386. These are characters/4 estimates, not tokenizer results. There is no always-on prompt hook in this pack. The offline competitor report includes its router injection separately.

## Unowned services

The plan assigns 163 groups / 8,887 leaves to skill owners. Ownership is a coverage map, not proof that every operation has a runnable workflow. The following 11 groups / 258 leaves remain unowned, reproduced by scripts/release_report.py:

| Group | Leaves | Future candidate, not current coverage |
|---|---:|---|
| marketplace-publisher | 111 | none |
| marketplace-private-offer | 27 | none |
| costad | 16 | cost analysis |
| demand-signal | 16 | none |
| mngdmac | 14 | none |
| cpg | 13 | compute |
| dif | 13 | none |
| gdp | 13 | none |
| ccc | 12 | compute |
| psa | 12 | networking |
| ddfs | 11 | none |

Dedicated Region/C3/Roving Edge/Alloy/media/iot are navigator routing rows only. The 101 thin and 19 gap certification leaves in research 10b are a coverage map, not a claim of completeness; those historical classification counts are outside the CLI ownership denominator and are not newly measured here.

## Validation boundaries and named gaps

D7 live evidence covers explicitly selected identity/scope, region, limits, usage, resource-search, namespace/buckets, shape/image/AD, VCN/subnet and metric-metadata reads, plus public pricing. The CLI report records 35 successful reads and 226 shape-only examples, with no failed attempt reclassified as empty. MCP selected checks passed. These are bounded samples from one API-key profile, one region and one commercial realm. Metadata success does not validate a provisioned workload, other signer modes, sovereign realms, multi-region behavior or large payloads.

Historical upstream discovery and successful reads are different outcomes. Compute/Identity/Usage/Limits initialization in research/data/oracle-mcp-smoke.json does not establish that their attempted operations passed. docs/oracle-mcp-research.json preserves that evidence; this pack's current smoke is separately recorded. No provisioning was done to fill coverage gaps.

Named research gaps carried forward:

- identity-domain federation depth (04b).
- the AWR id chain and the FSU discovery→cycle chain, asserted from --help, never run (11 §16).
- Console detail-page routes are convention only — a 200 from cloud.oracle.com proves nothing (12 B1/B4).
- no machine-readable Architecture Center index exists and dcterms.modified is unpublished, so freshness is a floor (13 §8).
- Oracle publishes no machine-readable error catalogue; message text is not a contract, branch on code+status (14 §17).
- no live injection test was performed; the 15 §9 strings are fixtures (15 §10).
- every PowerShell cell is a translation, not an executed command (16 §F).
- case.yaml grader key spelling is early-access blocked (17 §1/§6).

The offline description matcher misses its routing threshold. Model-backed task completion, leakage, live injection, confirmation behavior and behavioral no-plugin deltas remain unmeasured. The original live head-to-head gate is not satisfied by static descriptors. docs/validation-matrix.md names each red gate's reason and owner; there is no release-readiness claim.
