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
