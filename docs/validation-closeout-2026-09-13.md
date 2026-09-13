# Validation follow-up — September 13, 2026

The current 37-skill development repository is `jazzautomations/oci-agent-skills`.
This follow-up rechecks its release criteria without changing their thresholds.
The separate community repository has not received all subsequent development
repairs. Repository visibility and licensing remain unchanged.

## Fresh service and maintenance evidence

The [sanitized record](evidence/validation-closeout-2026-09-13.json) includes seven
scoped OCI reads and a read-only GitHub workflow check. No new model calls,
account mutations or resource provisioning are included.

| Criterion | Fresh observation | What closes it |
|---|---|---|
| V24 maintenance | The weekly workflow is active. GitHub returns no scheduled runs. Manual notification and duplicate handling retain their earlier evidence. | Observe a successful actual scheduled run. The next nominal trigger is September 15 at 06:17 UTC; dispatch timing is controlled by GitHub. |
| V25 service coverage | Cloud Guard is `DISABLED`; Support returns 403 with user and home region supplied. The bounded budget sample is empty; one cost-tracking tag exists; the selected settled regional cost window returns no rows. | Resolve service access and collect the missing scoped live evidence. Sufficient cost history, forecast and budget inputs are required for the affected FinOps checks. |
| V27 current task behavior | The existing full and five-case measurements are historical after source changes. A dry run confirms the full checked workflow requires 80 attempts: 40 tasks with and without the plugin. | Collect a new, separately budgeted full report, verify source fingerprints, answers, receipts and inert command syntax. This restricted fixture measurement does not by itself establish all original task semantics. |
| V28 native comparison | The earlier controlled comparison has 160 attempts, with every arm using the same synthetic MCP tool. | Run the originally specified native alternatives under the same task protocol and budget; reference text alone is not native product execution. |

An empty cost window is not proof of zero spend. A verified IAM email is not
proof of Support registration or user-group authorization. The latest user read
confirms a verified email but does not establish which Support prerequisite is
missing. Repeating these reads cannot enable a service or create billing history.

## Local validation

The full standalone suite passed **589 tests, three dependency warnings, in
61.85 seconds**. A separate installation/adapter run passed **20 tests, one
warning, in 70.76 seconds**. Template provenance, manifests, script/example
inventories, generated reader catalogs and recorded routing diagnostics also pass.

The first combined matrix attempt exhausted the workspace disk and was
interrupted. Regenerable npm/pip caches and completed installation-test temporary
copies were removed. The combined retry reported V14/V15 failures; both passed
in subsequent isolated runs. Its captured test output was discarded by the
existing runner, so the precise cause of those retry failures is not established.
A subsequent parallel rerun also passed both groups with unchanged timeout
limits: 589 tests and 20 installation tests. The
[raw combined matrix](evidence/validation-runner-attempt-2026-09-13.json) is
preserved, and the accepted matrix identifies the successful recheck evidence.

Fresh CLI-help lint passed without executing examples. All **180 public-link
checks** passed, including the expected negative fixtures. Other component and
historical-evidence subchecks passed. The accepted state remains **24 PASS,
two PARTIAL, one FAIL and one UNMEASURED**; no full-release criterion was waived.

The rerun sets `UV_LINK_MODE=symlink` for disposable dependency environments to
avoid repeated package copies. The installer still copies the distributed source;
the distribution gate inspects it for symlinks before runtime setup.

## Documentation repair

The review guide and roadmap previously retained obsolete history-cleanup
blockers, test counts and service observations. They now point to current
evidence. The preserved PDF and historical experiments remain dated snapshots.

All four release criteria remain open until their acceptance evidence exists.
The [release matrix](validation-matrix.md) distinguishes component checks,
historical measurements and actual current behavior.
