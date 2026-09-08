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
3–8. Pending.

Next exact step: generate script hashes/examples and enforce script provenance in the guard (item 3).
