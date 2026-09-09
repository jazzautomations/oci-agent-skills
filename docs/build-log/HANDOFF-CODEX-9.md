# HANDOFF 9 → Codex — two guard residuals + one README wording (post-merge polish on main)

Branch main. Same ground rules. One commit per item, pytest + validators green.
1. scripts/guard_lib.py:~189 whitelists only `${CLAUDE_PLUGIN_ROOT}/scripts/`; extend the sha-pinned plugin-script allow to
   `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/scripts/<file>` invoked with or without a `bash`/`python3` prefix, AND to the relative forms the
   SKILL.md Route tables actually print (`scripts/<file>.sh --help`, `skills/<skill>/scripts/<file>`), resolving relative paths against
   CLAUDE_PLUGIN_ROOT and matching by sha256 from catalog/scripts.json. Unknown/sha-mismatch stays `ask`. Tests for all forms.
2. README.md:~56 and docs/foundation.md: the V8 sentence "uses frozen research severity labels, separately from catalog verb labels" is
   overstated — tests/fixtures/guard-severity.json is the same taxonomy as catalog/cli.jsonl (5,437/5,437 identical), sha-pinned. Rewrite to:
   the matrix is measured against a sha-pinned severity snapshot derived from the same generator; the independent check is "zero allows
   fall outside the strict read-only set" (classify_leaf → ask whenever read_only is false), which is what the test asserts.
3. Remove stray `skills/*/.handoff-*.json|py` scratch files and add `skills/*/.handoff-*` to .gitignore. Refresh docs/validation-matrix.md
   via release_gate (diff mode) and commit. Final CODEX-STATUS.md. Do not push.
