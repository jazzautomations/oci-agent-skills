# Changelog

## Unreleased — presentation and documentation

Repaired semantic selection evaluation. The old lexical filter rejected 39 valid
requests before matching; it is retained as a diagnostic, while V19/V20 now check
dated, input-bound semantic trials with blind requests, pinned model and unchanged
thresholds. Tightened navigator, database-fleet and enterprise-application scope.
Two final trials score 79/80 and 77/80, with zero negative firings and 4/4 overlap
pairs in each; 12 additional scope regressions pass. CI verifies evidence rather
than making a new model call. Native host activation and task completion remain
unmeasured; all earlier failed trials are retained.

Expanded the Portuguese review PDF into a seven-page illustrated explanation:
network troubleshooting scenario, component architecture, nine coverage areas,
reproducible demo, scoped evidence and focused review questions. Added embedded
fonts and explicit text-frame overflow checks to the presentation generator.

Added a private technical review pack: Portuguese briefing PDF, five-minute
offline component walkthrough, recorded input hashes, feedback template and
an unsent introduction draft. The demo exercises catalog lookup, inert guard
classification and the actual MCP stdio server without cloud operations.

Fixed fresh-checkout CI template validation: verify a committed plan-derived
fingerprint without requiring ignored research files. Two regression tests cover
missing research, stencil drift and explicit regeneration inputs.

Organized reader documentation, machine-readable evidence and historical build
records. Added generated skill and MCP catalogs, a documentation index,
contributor guidance, security reporting and a roadmap with acceptance criteria.
Updated path consumers and copied-package documentation links. Identity and
governance helpers now list direct children by default, with explicit subtree
selection; malformed governance responses remain unreadable. The script harness
supplies a real offline policy fixture, uses the selected profile's user for
key-age checks and labels offline execution separately. Package manifests
remain at 0.2.1; the v2 skill-set name is not a 2.0.0 release claim.

## 0.2.1 — 2026-09-09, unreleased

Replaced the legacy skill set with 33 scoped skills, retired validation exemptions, regenerated script/example/guard artifacts, and populated full/database/DevOps marketplace subsets. Copy installers include shared references, hooks, runtime, MCP configuration, evals and license notices without source-tree symlinks or local scratch files.

Added D7-scoped CLI/MCP evidence, unchanged evaluation corpora in both supported task layouts, offline routing/negative/command/safety graders and four-arm static comparison. Published reproducible counts, actual guard behavior, historical/current denylist distinctions, source provenance and unowned services.

Release remains blocked by the description-routing threshold and unmeasured model-backed evaluations. The evidence does not establish live injection resistance or complete service coverage. No tenancy mutations were performed. The implementation has been integrated into main.
