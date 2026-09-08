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
8. Pending.

Next exact step: audit all W01–W08 done-when checks and finish the verification guide (item 8).
