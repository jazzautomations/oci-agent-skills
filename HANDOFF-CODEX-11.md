# HANDOFF 11 → Codex — skill `oci-finops-waste` (read-only waste finder) + demo report

Branch main of /root/projects/oci-agent-skills. Ground rules as always: read-only OCI (profile DEFAULT, us-chicago-1), generic repo,
every number reproducible, validators + pytest green per commit, commit per item, `git push origin main` at the end, CODEX-STATUS.md.
INPUTS (read fully before coding; they are the research, not the spec): research/18-finops-waste-finder.md (map + build spec),
research/22-finops-real-problems.md (real pains, Cloud Advisor overlap, false-positive traps), research/23-finops-deep-study.md
(detector spec table: pattern → commands → metric → threshold → savings formula with SKU → confidence). Also research/06c (price API),
skills/oci-cost-analysis (reuse its price lookup), skills/_TEMPLATE/SKILL.md, CONTRIBUTING.md, references/untrusted-output.md.
DELIVER (item 0 FIRST, it is a live defect in the shipped repo):
0. FIX the price extractor: `scripts/price.sh` / references/price-api.md / skills/oci-cost-analysis use `.currencyCodeLocalizations[0].prices[0].value`,
   which returns 0.00 for ~50 tiered SKUs (research/23 §price). Implement a band-aware lookup (given projected monthly quantity q, pick the band
   whose [rangeMin, rangeMax) contains q; flat SKUs have one band). Regression tests: B91628 → 0.0255 at q=100, B93030 → 0.0113 at q=1488,
   B91961 → 0.0255 flat. Also apply the research/22 "build changes" list: usage-api group-by cap is 4 (fix 00-PLAN line 270 mention only in
   docs, and the MCP cost tool schema + oci-cost-analysis reference), MONTHLY windows snapped to the 1st with echo assertion, reject TOTAL
   granularity, bound HOURLY (≤36h and start within 31 days), sort on time-usage-started and drop null/zero rows, no deltas over the last 48h,
   print covered window + currency with no FX, free-tier gate every finding (is-free-tier), never surface Cloud Advisor action.url, home
   region for `oci optimizer`, exponential backoff on 429, volume attachment from attachment lists not lifecycle-state, cost-reports path
   `reports/cost-csv/` + FOCUS (not `reports/usage-csv`). Add references/cloud-advisor.md (21-rule catalogue + thresholds from 22).
   Commit this as its own fix commit before starting the new skill.
1. skills/oci-finops-waste/SKILL.md per stencil (description ≤400 chars with Use when/Not for; mode read-only; metadata.verified per
   live evidence), references/detectors.md (the detector table with SKU ids and thresholds, each row sourced), references/false-positives.md.
2. skills/oci-finops-waste/scripts/waste_scan.py (+ .sh wrapper) via scripts/lib/oci_ro ONLY: enumerates candidates with resource
   search + service lists, pulls 14-day MQL P95 where needed, prices via the public price API (cache to .local), emits JSON + markdown
   report {finding, resource (name, OCID redacted to last 6), evidence, monthly_estimate, confidence, action (command to fix, marked
   MUTATING, never executed)}. Bounded: --compartment, --max-resources, --days. Every detector from 23's table that is read-only.
3. catalog/fragments/oci-finops-waste.json; tests (unit with mocked oci_ro outputs for each detector; a golden report); regenerate
   catalog (inventory.py --scripts --examples) and update docs/skills.md via scripts/doc-gen.
4. Run it live on this tenancy (expect at least: stopped instance still paying boot volume; missing budget; unattached/orphan volumes
   if any). Save a REDACTED sample to docs/evidence/finops-sample-report.md. Record live/partial in the skill footer.
5. docs/finops.md: what it detects, what Cloud Advisor already covers and how this differs (from 22), limits. README: one row + link.
