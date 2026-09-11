# Keeping cloud assumptions current

Three repository schedules cover different failure modes:

| Check | Schedule (UTC) | What changes trigger review |
|---|---|---|
| Cloud source freshness | Daily 07:43 | Sentinel OCI price bands, OCI CLI/SDK/driver releases, official sizing/migration/pricing API docs |
| CLI drift | Tuesday 06:17 | Required flags and upstream breaking-change notes |
| Documentation links | Daily 03:31 | Unavailable referenced pages |

Schedules are configuration until GitHub Actions actually runs them. A scheduled
[source check on September 11](https://github.com/jazzautomations/oci-agent-skills/actions/runs/34598437623)
ran and correctly failed on three changed sources, with no unavailable sources.
The nightly link schedule also completed successfully (run 34578046130).
This is evidence of these two scheduled deliveries, not the separate Tuesday CLI drift schedule.
A [manual hosted run](https://github.com/jazzautomations/oci-agent-skills/actions/runs/34461758903)
passed on 2026-09-10 with no changes or unavailable sources. Its downloaded report is
recorded in [hosted evidence](evidence/cloud-freshness-hosted.json). This validates the
workflow implementation, not future cron delivery.

September 11 review: the driver release is now 26.0.0. Its
[release notes](https://python-oracledb.readthedocs.io/en/latest/release_notes.html)
describe year-based versioning, removal of Python 3.9 and some Thick-mode/LOB
compatibility changes. The demo remains pinned to the live-tested 4.0.2; observing
the new release is not a driver upgrade or a claim that 26.0.0 passed live tests.
The changed migration specification includes OLVM targets and architecture
constraints; the repository does not gain OLVM execution support from this review.
The AWS instance-type reference still documents the CPU/core/thread and memory
fields used by the offline normalizer. A page hash cannot identify the exact
historical text delta because the old full page was not retained.
After review and the 463-test regression run, the observed-source baseline was
updated September 11. Dependency pins were not changed by baseline acceptance.
The freshness job downloads a fixed allowlist of public official sources. It compares
structured price/version facts and reference text fingerprints with a reviewed baseline.
Changes or unavailable sources fail the check and produce a report with direct review links.
A changed page is a review signal, not proof of a breaking API change. HTTP 200 alone is
not freshness. Source content is untrusted data and is never executed as instructions.

This gathers current evidence automatically; it does **not** perform autonomous semantic
research or rewrite the code. An agent or maintainer reviews linked source changes, checks
affected calculations/CLI help/fixtures, then explicitly accepts a new baseline. There is
no automatic commit, cloud mutation or external issue posting in this new workflow.

Price caches refresh after 24 hours. Fetch failure does not silently reuse stale prices:
scanners mark pricing unavailable; calculators stop. Explicit offline snapshots remain
available for reproducing an older estimate and are labelled as such. Snapshot publication
date and retrieval date have different meanings: an unchanged official price list can
have an old publication date even after a successful fresh fetch.

Quota, regional capacity, model retirement and database version availability depend on the
account/region. Run the demo preflight immediately before execution; a public documentation
monitor cannot certify those facts. Never treat a previous successful deployment as current
capacity evidence. Recheck source cloud contracts and discounts with the customer.

Review workflow: read the report → inspect official source → assess affected skills and
fixtures → validate → run `python scripts/ci/check_cloud_freshness.py --write-baseline`
after review. Keep the resulting diff with the associated code/documentation changes.
