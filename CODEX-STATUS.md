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
5–8. Pending.

Next exact step: copy the plan template with errata applied (item 5).
