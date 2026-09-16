# Contributing

Help make OCI workflows precise, reproducible and easy to inspect. Start with the
[skills catalog](docs/skills.md), [architecture](docs/foundation.md) and
[open work](docs/roadmap.md) to find the owner of a workflow before adding a skill.

## Set up

Use Python 3.13+, `uv` and OCI CLI 3.93.0. Keep OCI CLI in its own environment;
the locked MCP runtime does not install it. From the repository root:

```bash
uv sync --frozen --project runtime
uv run --frozen --project runtime oci-readonly-smoke
```

The smoke command requires no credentials and performs no cloud operations.
Credentials, local environments and research must remain outside the shipped tree.

## Add or improve a skill

1. Check existing ownership. Prefer improving the relevant skill over adding an
   overlapping trigger. Use [the stencil](skills/_TEMPLATE/SKILL.md.template) for a
   new `skills/<name>/SKILL.md`, and include `LICENSE.txt`.
2. Write a specific description with `Use when:` and `Not for:`. Supply scope,
   routes, bounded commands, failure modes and evidence labels. Keep the body
   within the enforced 200-line and 1,500 estimated-token budgets.
3. Link focused references only where needed. Keep shared guidance in
   `references/`; avoid loading whole manuals or duplicating shared contracts.
4. Compose OCI helper reads through `scripts/lib/oci_ro.sh` or `oci_ro.py`.
   Preserve explicit identity/region/compartment scope, bounded output and redaction.
   Do not execute mutation recipes during validation. Label them
   `# MUTATING — not run in this repo`, `[shape-verified]`, and provide a rollback.
5. Add examples to `catalog/fragments/<name>.json`. For a new skill, update the
   domain map in `scripts/doc-gen/catalogs.py` and relevant marketplace selections.
   Record syntax-only and live evidence separately, with dates and prerequisites.
6. Add behavioral regressions for substantive code changes. Keep evaluation
   labels separate from selection logic; do not tune against expected case IDs or
   weaken thresholds to obtain a passing report.

Regenerate derived artifacts after edits:

```bash
python3 scripts/inventory.py --scripts --examples
uv run --frozen --project runtime python scripts/doc-gen/catalogs.py
```

CLI census regeneration requires Python from the pinned OCI CLI environment:
`python scripts/inventory.py --format jsonl --index --check`. It inspects installed
command definitions; it does not call OCI services.
The optional command checker also requires
`python scripts/generate_read_contracts.py --check` in that environment. After a
reviewed CLI-catalog update, regenerate its aliases and enums with the same
command without `--check`; never hand-edit `catalog/read-contracts.json`.

## Validate

```bash
uv run --frozen --project runtime pytest -q tests skills/oci-incident-triage/tests skills/oci-security-posture/tests skills/oci-sdk-patterns/tests
uv run --frozen --project runtime python scripts/ci/check_frontmatter.py
uv run --frozen --project runtime python scripts/ci/check_refs.py
uv run --frozen --project runtime python scripts/ci/check_portable.py
uv run --frozen --project runtime python scripts/ci/check_budget.py
uv run --frozen --project runtime python scripts/ci/check_licenses.py
uv run --frozen --project runtime python scripts/ci/check_no_secrets.py
uv run --frozen --project runtime python scripts/ci/check_scripts_readonly.py
uv run --frozen --project runtime python scripts/ci/check_template.py
python3 scripts/ci/check_manifests.py
python3 scripts/inventory.py --scripts --examples --check
uv run --frozen --project runtime python scripts/doc-gen/catalogs.py --check
uv run --frozen --project runtime python scripts/ci/lint_fences.py --live-help
uv run --frozen --project runtime python evals/run_routing.py --negatives
uv run --frozen --project runtime python scripts/eval/routing_diagnostics.py --check evals/results/routing-diagnostics.json
```

`--live-help` executes only CLI help, never a documented operation. Native plugin
validation additionally uses `claude plugin validate . --strict` and
`claude plugin validate ./skills --strict` where that host is installed.

`uv run --frozen --project runtime python scripts/ci/release_gate.py` runs the
full matrix and writes candidate reports outside the checkout. Review its diffs
before updating evidence. Existing live-coverage and host-evaluation
gaps remain stable-release blockers; a nonzero exit is expected until they are resolved.
The owner-authorized public preview documents these failures without waiving them.
The default gate replays recorded host evidence without inference. `--probe-host`
is a potentially paid opt-in, requiring separate model-provider budget approval;
OCI credits and ordinary CI validation do not authorize it.
Public-link checks run separately from offline checks. Semantic selection uses
dated model evidence checked in CI; after changing descriptions, the corpus or
the collector policy, recollect both semantic reports as described in
[the evaluation guide](docs/evals.md). Missing or stale evidence fails the gate.

Template checks use the committed `scripts/ci/template-source.json` fingerprint,
so a clean clone needs no private research. To revise the authoring stencil from
a reviewed plan, use `python3 scripts/ci/check_template.py --plan PATH --write`;
review both the template and provenance diff, then regenerate the script registry.

## Preserve behavioral evidence during repairs

Six older task reports are pinned in `evals/historical-evidence.json` and replayed
with their original offline verifiers from fixed, allowlisted local Git revisions. Keep full
history available. Report `current_sources: false` as historical evidence, never
as validation of changed skills. Modified reports cannot use this replay path.
Do not edit frozen collectors or overwrite reports to raise scores. A new
measurement needs its own path and current source fingerprints; a targeted
regression does not replace the full task matrix. See
[the repair protocol](docs/task-repair-validation-2026-09-11.md).

## Inspect the installation

```bash
bash installers/install.sh --target /tmp/oci-plugin-review --host claude --copy-shared
```

Choose an absent or empty target outside the checkout. Inspect it before starting
`uv`: it should contain no symlinks, credentials, research or build notes. Shared
references, helpers, catalog, runtime and notices must remain usable together.
Authoring-only documentation links point back to the source repository.

## Submit a change

Explain the concrete problem, resulting behavior and checks performed. Distinguish
offline tests, CLI syntax checks and dated cloud evidence. Preserve current user
work and keep unrelated generated changes out of the diff. See
[SECURITY.md](SECURITY.md) for security reports and the [audit](docs/audit.md) for
license provenance and coverage limits.
