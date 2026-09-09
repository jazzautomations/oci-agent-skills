# Handoff 2 progress

Branch: `v2-foundation`. No tenancy mutations; protected content remains unchanged.

1. Done: pure sanitizer, JSON delimiters/ASCII escaping, per-field codepoint budgets,
   control/bidi flags, advisory matching, and all ten research injection fixtures.
   Values remain visible. `clean(clean(x))` preserves its result and flags; cleaning
   the returned text again preserves the text. Ordinary non-strings pass through.
   Verification: `uv run --frozen --project runtime pytest -q tests`.
2. Done: Console URL builder, shipped airport-region map, IAM region omission,
   bucket/subnet requirements, stable query order, and convention warnings.
   Verification: `uv run --frozen --project runtime pytest -q tests`.
3. Done: deterministic script SHA256 registry bound into generated guard policy;
   unknown/changed scripts ask; fragment merge rejects duplicate ids; non-OCI hand
   rules remain explicitly unmeasured. Shared wrapper now has pure check(), JSON
   output, bounded reads, file-JSON resolution/recheck, service error envelopes,
   sanitation/redaction and explicit trace/all switches. No mutations executed.
   Verification: `python3 scripts/inventory.py --scripts --examples --check`;
   `uv run --frozen --project runtime pytest -q -s tests/test_guard.py`;
   `uv run --frozen --project runtime pytest -q tests`.
   Plan discrepancy retained: supplied purge regex gives destructive 1/997/328,
   not the stated 2/996/328; all 9,145 leaves replayed, 278 CRITICAL denied.
4. Done: all nine CI validators, nightly links, Tuesday CLI/required-flag drift,
   mutation marker/rollback lint, portable metadata, verified enum, reference
   routing checks (non-Markdown exempt), budgets and license checks.
   Installed-host paths probe found descriptions available regardless of paths;
   no added body activation observed. Evidence: scripts/ci/paths-probe.json.
   Strict content failures are recorded, not claimed green: 34 frontmatter,
   34 portable, 29 reference, 2 budget, 17 license findings at this snapshot.
   Ownership prevents fixing real skills/references/root LICENSE here.
   Verification: `uv run --frozen --project runtime pytest -q tests`;
   validator commands and baseline regeneration documented in docs/foundation.md.
5. Done: exact plan §4.1 stencil with only the overriding B3 canonical
   references/error-corpus.json path and N3 partial enum applied. It is an
   intentionally non-runnable placeholder template; content linters exempt it.
   Verification: `python3 scripts/ci/check_template.py` (requires local plan);
   `uv run --frozen --project runtime pytest -q tests`.
6. Done: 15 shipped tools (14 credentialed + oci_price_lookup, credential-free),
   provenance {source, trust, complete}, shared field sanitation with flags,
   ASCII JSON text serialization, descriptive error results, and D7-only live smoke.
   Offline schema estimate: 3,455 tokens (13,820 characters / 4, rounded up).
   D7 live smoke: all 12 checks passed on 2026-09-08; five tools explicitly
   shape-only. No mutation or broader-scope retry was run.
   Verification: `uv run --frozen --project runtime oci-readonly-smoke`;
   `OCI_CONFIG_PROFILE=DEFAULT uv run --frozen --project runtime oci-readonly-smoke --live --region us-chicago-1`;
   `uv run --frozen --project runtime pytest -q tests` (includes <100 ms responsiveness).
7. Done: W08a Claude/Codex manifests, three marketplace entries with hooks and
   no skills arrays, install/docs, unguarded-host refusal, manual argv preflight,
   self-contained shared-reference copies, and host stdio launch tests.
   The copied distribution excludes the placeholder template, research/vendor
   and environments. It contains no symlinks before runtime initialization.
   Literal source `find . -type l` remains nonempty due to pre-existing protected
   research links and generated runtime/.venv links; neither is distributed.
   Root strict validation sees the deliberately invalid placeholder stencil;
   W08b content selection and release licensing remain deferred per errata.
   Verification: `python3 scripts/ci/check_manifests.py --host-validation`;
   `uv run --frozen --project runtime pytest -q tests`.
8. Done: reconciled docs/foundation.md with the final implementation and exact
   verification commands; documented W42a regeneration and all remaining gates.
   Final audit added the canonical lib/redact entry point, exhaustive wrapper
   replay, bounded required/query catalog forms, per-row scope disclaimers,
   operation-like profile/auth value cases, Git-history scan and changelog drift
   matching. Reference link evidence is scripts/ci/link-check-report.json.
   Verification: `uv run --frozen --project runtime pytest -q tests`: 201 passed;
   Ruff and whitespace checks passed. Full skills/docs/README live-help fence
   check passed. All 33 examples passed offline Click validation. CLI regeneration
   was byte-identical. Reference links: 23 HTTP 200 plus 5 expected 404, all passed.
   Source and Git-history heuristic secret scans found no matches.

## Final W01–W08 done-when exceptions and next owner actions

All eight handoff items have been processed and committed individually. Remaining
release/content gates are explicit; this is not a claim that every PLAN gate is green.

- **W01 policy-count conflict:** strict D3 allows 3,601 snapshot leaves, not all
  3,708 census-labelled reads. Accepting the latter would contradict the specified
  verb allowlist. All 9,145 leaves are tested against the stricter policy.
- **W02 matrix conflict:** verbatim purge rules produce destructive 1/997/328,
  not the plan's 2/996/328. The actual matrix is published, with all 278 CRITICAL
  leaves denied. The advisory hook asks for unresolved file JSON; execution alone
  resolves bounded scalar JSON and rechecks it. It does not load arbitrary JSON
  files merely to inspect a proposed shell command.
- **W04 protected content:** the shared library is still being written by its
  owner (library incomplete at this audit versus the final 15). Its completion,
  source-to-reference unverified-tag retention proof, and content corrections
  were not performed here because references/ and research/ are prohibited.
  The observed reference URLs passed; that does not validate future additions.
- **W05 strict content gates:** the final explicit baseline contains 34
  frontmatter, 34 portable, 35 reference, 2 budget and 17 license findings.
  The over-budget references at this snapshot are console-links.md, untrusted-output.md. Existing skill descriptions/statuses/routing and licenses
  belong to content owners. Root LICENSE remains MIT; Apache-2.0 publication
  metadata is planned, not a relicense. These protected files were not edited.
  CI checks exact baseline equality; new and stale exceptions fail. The reference
  owner is actively adding files, so this snapshot can change immediately after
  this audit and must be refreshed when that content is finalized. Every utility
  that never calls OCI is exempt from meaningless wrapper-import requirements;
  actual OCI execution is confined to the wrapper. Static checks are not a proof
  about arbitrary executable code.
- **W05 paths evidence boundary:** installed Claude Code 2.1.263 does not gate
  description availability on paths. Added body activation was not observed;
  no claim is made about other versions/hosts. No edits to the six real skills
  were warranted or permitted. Evidence and rerun command are in docs/foundation.md.
- **W06/W07:** offline regressions, responsiveness, 15-tool schema and D7 live
  smoke are green. Other auth modes, regions/realms and five out-of-D7 tools are
  explicitly shape-only; no broader live exercise is claimed.
- **W08 source-tree versus distribution gate:** literal `find . -type l` is
  nonempty due to pre-existing protected research links and runtime/.venv links.
  The copied distribution excludes both and passes a no-symlink check before
  runtime setup. The required raw placeholder template is not valid skill YAML,
  so source-root/bare-skills strict validation cannot pass while it is present.
  The copied plugin excludes it and passes installed Claude strict validation.
  Final marketplace skills arrays and final-content validation belong to W08b
  per ERRATA B2; no arrays were populated prematurely.
- Hosted nightly/Tuesday workflows were implemented and their logic tested;
  no GitHub workflow dispatch or issue publication was performed in this session.

Next exact steps are for the content/release owners: complete W04 and W09–W41,
resolve the recorded content/license findings, then run
`python3 scripts/inventory.py --scripts --examples` once as W42a, review/refresh
the content baseline, and finish W08b. New skill scripts ask until W42a binds them.

No OCI tenancy mutation was run. No changes were made to references/, research/,
real skills, README.md or root LICENSE. The other engine's untracked references/
work is intentionally excluded from these commits.

## Handoff 4 — resumed validation (2026-09-09)

The first seven skills were already committed through `7356b1f` (oci-ai-services). The remaining four are validated and committed individually below, with their catalog fragments. Live scope is the explicitly selected existing API-key profile, us-chicago-1, tenancy root, without recursive traversal. No tenancy mutations executed.

### oci-data-platform

- All seven handoff linters passed, including `lint_fences.py --live-help`; generic quick validation rejects the stencil-required compatibility key. The declared Apache-2.0 LICENSE.txt is supplied.
- Fragment: 8 examples match Commands exactly and pass installed Click validation.
- Full pytest: 2 failed, 199 passed, 1 warning in 41.63s.
- Live: all ten identity/scope, shape/image/AD, VCN, namespace, vault and monitoring metadata probes passed; three ADs discovered. No identifiers or raw resource values retained.
- Domain evidence: shape-only: domain APIs not run; no workload execution or provisioning.
- All 3 linked Oracle documentation pages returned HTTP 200.
- Exceptions: full-suite catalog regeneration and the fixed 16-skill installer assertion fail outside ownership; W42a and test-owner work remain. Repository licensing also has findings outside this skill. All §3.2 files, mode, exact description and canonical no-script line are present; domain workloads remain unexecuted because no provisioned validation targets were supplied.
- Details: [skill status](skills/oci-data-platform/CODEX-STATUS.md), [validation evidence](skills/oci-data-platform/validation-evidence.json).

### oci-dr-backup

- All seven handoff linters passed, including `lint_fences.py --live-help`; generic quick validation rejects the stencil-required compatibility key. The declared Apache-2.0 LICENSE.txt is supplied.
- Fragment: 8 examples match Commands exactly and pass installed Click validation.
- Full pytest: 2 failed, 199 passed, 1 warning in 35.28s.
- Live: all ten identity/scope, shape/image/AD, VCN, namespace, vault and monitoring metadata probes passed; three ADs discovered. No identifiers or raw resource values retained.
- Domain evidence: partial: Commands availability-domain list ran live; DR, backups, snapshots and instance placement remain shape-only.
- All 3 linked Oracle documentation pages returned HTTP 200.
- Exceptions: full-suite catalog regeneration and the fixed 16-skill installer assertion fail outside ownership; W42a and test-owner work remain. Repository licensing also has findings outside this skill. All §3.2 files, mode, exact description and canonical no-script line are present; domain workloads remain unexecuted because no provisioned validation targets were supplied.
- Details: [skill status](skills/oci-dr-backup/CODEX-STATUS.md), [validation evidence](skills/oci-dr-backup/validation-evidence.json).

### oci-migration-patching

- All seven handoff linters passed, including `lint_fences.py --live-help`; generic quick validation rejects the stencil-required compatibility key. The declared Apache-2.0 LICENSE.txt is supplied.
- Fragment: 8 examples match Commands exactly and pass installed Click validation.
- Full pytest: 2 failed, 199 passed, 1 warning in 44.82s.
- Live: all ten identity/scope, shape/image/AD, VCN, namespace, vault and monitoring metadata probes passed; three ADs discovered. No identifiers or raw resource values retained.
- Domain evidence: shape-only: domain APIs not run; no workload execution or provisioning.
- All 3 linked Oracle documentation pages returned HTTP 200.
- Exceptions: full-suite catalog regeneration and the fixed 16-skill installer assertion fail outside ownership; W42a and test-owner work remain. Repository licensing also has findings outside this skill. All §3.2 files, mode, exact description and canonical no-script line are present; domain workloads remain unexecuted because no provisioned validation targets were supplied.
- Details: [skill status](skills/oci-migration-patching/CODEX-STATUS.md), [validation evidence](skills/oci-migration-patching/validation-evidence.json).

### oracle-enterprise-apps

- All seven handoff linters passed, including `lint_fences.py --live-help`; generic quick validation rejects the stencil-required compatibility key. The declared Apache-2.0 LICENSE.txt is supplied.
- Fragment: 8 examples match Commands exactly and pass installed Click validation.
- Full pytest: 2 failed, 199 passed, 1 warning in 45.11s.
- Live: all ten identity/scope, shape/image/AD, VCN, namespace, vault and monitoring metadata probes passed; three ADs discovered. No identifiers or raw resource values retained.
- Domain evidence: shape-only: domain APIs not run; no workload execution or provisioning.
- All 3 linked Oracle documentation pages returned HTTP 200.
- Exceptions: full-suite catalog regeneration and the fixed 16-skill installer assertion fail outside ownership; W42a and test-owner work remain. Repository licensing also has findings outside this skill. All §3.2 files, mode, exact description and canonical no-script line are present; domain workloads remain unexecuted because no provisioned validation targets were supplied.
- Details: [skill status](skills/oracle-enterprise-apps/CODEX-STATUS.md), [validation evidence](skills/oracle-enterprise-apps/validation-evidence.json).

### Reference trim and completion

- Skill commits: `bf3e425` oci-data-platform; `951ba17` oci-dr-backup; `47be2c2` oci-migration-patching; `d94e4a6` oracle-enterprise-apps. Each includes its own catalog/fragments/<name>.json, fresh validation evidence and this status update.
- Reviewed and retained the existing wording trims: references/jmespath.md is **4,778 bytes ≤4,780**; references/realms-endpoints.md is **5,554 bytes ≤5,560**. Redundant introductions/wording were shortened; facts remain in the body. Exact comparisons against HEAD confirm no URLs, verification tags, table rows or fenced examples changed.
- All seven scoped reference validator invocations passed (frontmatter/portable have no applicable SKILL.md input). Template and manifest checks also passed. All commit whitespace checks passed.
- references/auth-modes.md is unchanged from the start of this resumed work (6,339 bytes); its pre-existing uncommitted trim is retained.
- Every skill's fresh full pytest run had **199 passed, 2 failed**. Remaining failures are tests/test_catalog.py::test_generated_scripts_and_fragments (W42a regeneration) and tests/test_installer.py::test_installed_copies_and_refs (hard-coded 16 skills). No unrelated tests or generated catalogs were changed to hide those failures. The latest run also exercised the reference contents committed here.
- Additional validator boundaries: the generic skill-creator validator rejects the repository-required compatibility key; repository frontmatter and portable validation pass. The four owned skill licenses are now present; root/other-skill licensing remains outside this task.
- No tenancy mutations executed. None of the other engine's skill directories or fragments were edited or included in these commits.

## Handoff 5 — Wave 2 batch A (2026-09-09)

Implemented and committed all 11 skill packages individually on `v2-foundation`, including their fragments. Applied the supplied findings for eight packages and independently reviewed security-posture, free-tier and SDK-patterns. **The strict repository-wide green gate is not met:** the existing two pytest failures and unrelated global validator debt remain below. These are reported, not hidden by a refreshed baseline.

No mutating OCI operation was executed. Live reads used the explicitly selected existing API-key profile in us-chicago-1, with tenancy-root/compartment scope taken from its local config. Audit/log checks used bounded recent windows; the Free Tier metric window was seven days. Public documentation, prices and specs used credential-free GETs. No tenancy identifiers, names, logs, keys or raw resource payloads were added to Git.

### Per-skill results

Each row passed all eight scoped checks: frontmatter, portable metadata, references, token budget, secrets, read-only scripts, fenced OCI commands with fresh `--help`, and Oracle documentation links. Descriptions compare exactly to the §3.2 rows. All 11 packages contain Apache-2.0 LICENSE.txt matching their declared metadata; root licensing remains separate.

| Skill | Commit | Fragment rows | Fixes and live evidence |
|---|---|---:|---|
| `oci-navigator` | `7c2b06a` | 10 | Corrected Email data-plane routing; added license; bounded Search evidence and partial verification. **Live:** Four successful reads; Fusion family list returned 404. Search bounded at 50; Email configuration available. |
| `oci-cli-auth` | `3a8789d` | 5 | Fixed dead work-request URL, wrong corpus citation, expired-session claim and untrusted-output link; explicit profile/config handling and failed-read exit status. **Live:** All five fences succeeded; whoami succeeded and list_all returned 44 regions with complete=true. |
| `oci-tenancy-governance` | `8a897ad` | 7 | Added the missing untrusted-output reference and aligned the skill license with its metadata. **Live:** All seven reads succeeded. Governance helper completed six reads with no unreadable scope. |
| `oci-iam-policy` | `6c59523` | 7 | Removed IAM/limits misrouting, corrected missing-endpoint behavior, required the documented environment for live policy linting, and qualified propagation evidence. **Live:** All seven reads succeeded. Live policy lint read one statement and returned advisory findings (exit 1), not a transport failure. |
| `oci-support-limits` | `e9707ec` | 17 | AD is optional for region-scoped limits and supplied only when applicable; both scope variants tested. Six mutation fences have rollback comments. **Live:** Definitions, values and question list succeeded. Capacity helper returned three successful envelopes for both REGION and AD limits. |
| `oci-logging-audit` | `8f3824d` | 7 | Replaced invalid bin/=~/top/rename grammar, corrected nested-field and scope syntax guidance, retention claims and Audit envelope description; documented JSON helper. **Live:** Both log searches and Audit returned rows; no customer log groups. Audit helper succeeded; six corrected query variants parsed live. log-list success remains shape-only. |
| `oci-incident-triage` | `efcd0e0` | 15 | Ten calls in actual step order; filters read methods/operations from write candidates; failed steps exit 1 with ok=false; fixed relative link, variables, help and corpus citations. **Live:** Seven fences succeeded. Ten-step script exited 1 with Cloud Guard/Support gaps; no degraded resource or LB was simulated. |
| `oci-security-posture` | `b35775e` | 29 | Independent review: scoped Search, explicit tenancy variable, ambiguous 404 handling, TCP ranges/all protocols/IPv6 severity, pseudonymous report labels and invalid age handling. **Live:** Five fences succeeded; Cloud Guard 404. Posture helper completed, including key-age read; 30 advisory findings, no resource names retained in this status. |
| `oci-cost-analysis` | `a1925cb` | 10 | Fixed flat object-list projections and false empty-report evidence, UTC-midnight forecast precision, Windows arithmetic, TOTAL help description and unverified throttling tags. **Live:** All five fences succeeded; FOCUS and classic CSV listings nonempty, budgets empty. Two-window helper and public price helper succeeded. |
| `oci-free-tier` | `c154196` | 8 | Independent review: daily metric samples retained across the full window; no claim that one daily percentile proves seven-day eligibility; qualified PAYG capacity/reclamation claims and stopped-ADB attribution. **Live:** All five fences and all five helper reads succeeded. Metrics empty; no reclamation or account lifecycle was triggered. |
| `oci-sdk-patterns` | `9ecdca8` | 5 | Independent review: selected auth/config forwarded explicitly, missing profiles cannot guess instance principal, fixed circuitbreaker import and pagination signature, guarded inference examples, refreshed hash-resolved specs and six-mode/four-language routing matrix. **Live:** All five CLI reads and both explicit API-key probe reads succeeded. Public Identity spec resolved and cached; no SDK write recipe or other signer was executed. |

### Verification and source corrections

- Final suite: **206 passed, 2 failed**, one dependency deprecation warning. The seven added regression tests pass. The two failures are unchanged from the start of the handoff: `tests/test_catalog.py::test_generated_scripts_and_fragments` (W42a artifacts stale) and `tests/test_installer.py::test_installed_copies_and_refs` (hard-coded 16 skills). Every initial skill commit had a fresh full root test run with 199 passed and those same two failures. Final fragment additions were checked together with the final full suite before being folded into the owning commits.

- All **120 fragment rows** resolve to installed CLI 3.91.0 leaves with required options; IDs are unique within the batch. Coverage includes each fenced read leaf in the skill and its references. Validation checked root-level options separately and allowed the documented environment placeholders. This is not a claim that the stock `check_examples.py` accepts these fragments: its narrow placeholder/global-option handling and merged-artifact input remain W42a integration work.

- The Windows source research arithmetic is wrong: the public B88318 rate is 0.092 per OCPU-hour, so 2 × 730 hours is 134.32, not 67.16. Both shipped references now use the corrected figure. Forecast with 2026-10-15T12:30:00Z returned InvalidParameter/400; 2026-10-15T00:00:00Z succeeded, disproving the month-alignment remedy.

- The Logging specification and live parses confirm rounddown, wildcard comparison, top-by and select aliases. A 14-day search span is not a retention limit. API field paths and whole quoted dotted keys are distinct. SDK 2.185.0 introspection confirms `CircuitBreakerError` comes from `circuitbreaker`, and pagination takes record_limit before page_size.

- Live findings are bounded samples, not inventories or compliance certification. Other SDK signers/languages, successful Cloud Guard/Support bodies, provisioned VSS/Data Safe/zone resources, actual incidents and all mutations remain unverified end to end. Generic 404s are retained as ambiguity, not proof of absence.

- Oracle documentation link checks passed, including negative fixtures. Additional public documentation links were reachable; Cloud Customer Connect returned HTTP 403 to this checker and remains accessibility-unverified. Example API endpoint roots and placeholders are not documentation links.

- The scripts retain the repository convention of unconditional JSON (some shell composers emit JSON Lines); new/updated Python entrypoints accept --json where useful. No repo-wide CLI-interface rewrite was attempted. Navigator intentionally composes shared helpers instead of a local script.

### Reproduce the checks

Run from the repository root, substituting the skill name:

```bash
uv run --frozen --project runtime python scripts/ci/check_frontmatter.py skills/oci-sdk-patterns
uv run --frozen --project runtime python scripts/ci/check_portable.py skills/oci-sdk-patterns
uv run --frozen --project runtime python scripts/ci/check_refs.py skills/oci-sdk-patterns
uv run --frozen --project runtime python scripts/ci/check_budget.py skills/oci-sdk-patterns
uv run --frozen --project runtime python scripts/ci/check_no_secrets.py skills/oci-sdk-patterns
uv run --frozen --project runtime python scripts/ci/check_scripts_readonly.py skills/oci-sdk-patterns
uv run --frozen --project runtime python scripts/ci/lint_fences.py skills/oci-sdk-patterns --live-help
uv run --frozen --project runtime python scripts/ci/check_links.py skills/oci-sdk-patterns
uv run --frozen --project runtime pytest -q tests skills/oci-incident-triage/tests skills/oci-security-posture/tests skills/oci-sdk-patterns/tests
```

For live helper checks, set the documented profile, region and scope variables explicitly; use each helper’s --help. `capacity.sh` was tested with custom-image-count and no AD, then standard-a1-core-count with a selected AD. Repeating reads does not require provisioning targets.

### Remaining repository-wide gates

- Root validators still report 28 frontmatter findings, 28 portable findings, 20 reference findings, 2 budget findings, 21 license findings and 2 script-registry findings. None names an owned batch-A skill. Budgets concern total legacy-plus-v2 descriptions and the shared untrusted-output cap; the latter still predates ERRATA N10. Reference checks do not yet recognize the N11 service-command-cards addition.

- Global secret scanning, Git-history secret scanning, template comparison and manifest validation pass. Generated scripts/examples/guard binding and baseline retirement belong to W42a; final skill selection and installer expectations belong to the integration/release work. Generated catalogs, root license and other owners’ content were left unchanged.

- Preserved the pre-existing uncommitted `references/auth-modes.md` edit byte-for-byte and the three oracle-autonomous-db `.handoff-*` files. They are not part of these commits.

## Handoff 6 — Wave 3 (2026-09-09)

### Package 1 — retire v1 and enforce strict gates

Removed the 13 named v1 directories and fragments; 33 v2 skills remain. Retired all baseline exemptions and removed CI baseline arguments. Applied ERRATA N10/N11 budgets and routed the shared command cards. Supplied Apache-2.0 licenses consistently, preserving the original MIT notice in NOTICE. Installer excludes private handoff scratch files and includes NOTICE. Preserved the pre-existing auth-modes edit and untracked handoff files outside this commit.

To satisfy the required green gate for this cleanup commit, pulled forward the mechanical W42a artifact regeneration and 33-skill test count; updated the catalog query regression to the surviving IAM skill. W42a still owns installed-Click example validation and repeat regeneration evidence.

Validation: full root plus three skill regression suites passed (208 tests); all strict content linters, template, manifests, fence lint and history scan passed. Commands: `uv run --frozen --project runtime pytest -q tests skills/oci-incident-triage/tests skills/oci-security-posture/tests skills/oci-sdk-patterns/tests`; each `scripts/ci/check_{frontmatter,portable,refs,budget,no_secrets,licenses,scripts_readonly,template,manifests,history}.py` and `scripts/ci/lint_fences.py` through the same Python environment. No tenancy operations executed.

### Package 2 — W42a regeneration and examples

Installed CLI 3.91.0 accepts all 254 examples spanning all 33 skills without executing callbacks. The checker now recognizes installed root options and the explicit v2 placeholder vocabulary; live authorization remains separate. Added a callback-free global-option regression. Script registry and guard hash binding regenerated; a second generation is byte-identical across scripts.json, examples.json and guard.json. Full suite: 209 passed; all strict linters green. Reproduce examples using the Python environment that contains pinned oci-cli: `python scripts/check_examples.py`; regenerate with `python scripts/inventory.py --scripts --examples` and verify with `--check`. The runtime environment does not itself include oci-cli.
