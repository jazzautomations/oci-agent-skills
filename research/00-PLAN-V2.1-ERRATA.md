# PLAN v2.1 — ERRATA (coordinator resolutions, 08/09/2026, final)
Read together with research/00-PLAN-V2.1.md. Where they differ, THIS file wins.

## Blocking fixes
B1 Generated artifacts. `catalog/*` is GENERATED-ONLY. No Wave-2 skill package edits any file under `catalog/`.
   Each skill package writes its example rows to `catalog/fragments/<skill>.json` (schema = examples.json row) and its
   scripts under `skills/<skill>/scripts/`. A new package W42a "Regenerate" (Wave 3, deps W09–W41) runs
   `scripts/inventory.py --scripts --examples` ONCE to build `catalog/scripts.json` (sha256 per plugin script),
   merge fragments into `catalog/examples.json`, and re-sign `catalog/guard.json`. Ownership: `catalog/guard.json`
   is written by W02 (guard) and consumed by W03; edge W03→W02 added (W02 tests use scripts.json fixture).
   Until W42a runs, the guard's plugin-script rule treats scripts under `skills/*/scripts/` as "unknown ⇒ ask"; that is expected mid-build.
B2 W08 split. W08a (Wave 1): manifests, install.sh, docs/install.md, docs/mcp-optional.md; marketplace.json entries carry
   NO `skills[]` arrays yet; gate = schema validity + launchers start over stdio. W08b (Wave 3, deps W09–W41):
   populate `skills[]` (33 / 8 db / 9 devops) and pass `claude plugin validate . --strict` and `./skills --strict`.
B3 error-corpus canonical path. Shipped copy = `references/error-corpus.json` (generated from
   `research/data/error-corpus.json` by W04; regeneration command documented in references/error-triage.md).
   The §4.1 template and every skill cite ids from `references/error-corpus.json`. `check_refs.py` exempts
   non-`.md` files from the name-or-delete rule. `research/` and `vendor/` do NOT ship with the plugin.

## Non-blocking decisions
N1 Always-resident floor published as "≈6.3–6.5k tokens (≈3,020 descriptions + ≈3,300–3,500 MCP schemas, estimates)". Same string everywhere.
N2 `paths` key: present on 6 rows (oci-oke, oci-devops-pipelines, oci-serverless, oci-terraform, oracle-db-vector-ai, oracle-apex).
   If W05 proves `paths` GATES activation, remove it from all 6; if it only ADDS, keep all 6.
N3 `metadata.verified` enum = `live | partial | shape-only`; `partial` = "some Commands ran live in the reference tenancy, listed in the skill's Failure modes footer".
N4 Six no-script skills carry the same canonical line: "No script: every read here is a single CLI call already covered by scripts/lib/oci_ro; nothing to compose." (oracle-db-fleet, oci-ai-services, oci-data-platform, oci-dr-backup, oci-migration-patching, oracle-enterprise-apps)
N5 MCP: "15 shipped tools (14 credentialed + oci_price_lookup, credential-free)". Ordering line in §5 is derived from the deps column.
N6 W44 imports research/17 §5 fairness rules only; metric constants come from v2.1 §2.9/§6.2 (V19 routing, V20 negatives).
N7 §1.2/§1.3 references to "W20/V16" are v2 numbering.
N8 W04: 15 files (14 rows; `resource-type-families.json` is hand-derived from research/04b §1–14; say so in the file header).
N9 Deferrals confirmed intentional: Dedicated Region/C3/Roving Edge/Alloy/media/iot = navigator routing rows only; 11 unowned groups (258 leaves) published in docs/audit.md; identity-domain federation and all PowerShell cells ship `[unverified]`.

## Build reality (what already exists on branch v2-foundation, by Codex, commits ce20ae3..4fcec4d)
W01-ish: scripts/lib/oci_ro.{sh,py} + redact; W02-ish: scripts/guard_oci.py + guard_lib + hooks/hooks.json + full leaf replay;
W03-ish: catalog cli.jsonl/cli-read.jsonl/index.json + scripts/catalog.py + inventory.py --format jsonl --index;
W05-ish: skills/_TEMPLATE + scripts/ci/{check_frontmatter,check_refs,lint_fences,check_no_secrets} + CI; W06+W07-ish: MCP 14 tools, auth TTL, async, subtree allowlist, compartment_depth;
W08a-ish: installers/install.sh copy-only + .mcp.json + docs/foundation.md. Tests: 165 passing. See docs/foundation.md and CODEX-STATUS.md.
Gaps vs v2.1 Wave 0/1 are closed by HANDOFF-CODEX-2.md (code) and the references workflow (content).
