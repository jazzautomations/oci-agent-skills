# Roadmap and release criteria

The v2 skill set ships as package **0.2.1 preview**. The next release requires
closing the [validation matrix](validation-matrix.md), not merely renaming the
version or increasing the skill count. All current evidence is scoped and dated.

| Work | Acceptance evidence | Owner / prerequisite |
|---|---|---|
| V19 routing | Meet the existing ≥90% gate with a valid evaluation method; keep negatives at zero and selection independent of expected labels | Evaluation/routing maintainers |
| V22 history hygiene | Reviewed cleanup of reachable historical patch content; current-file and full-history scans pass | Repository owner; published-history coordination |
| V24 hosted drift | Capture a hosted scheduled run and exercise issue creation without duplicate issues | CI maintainers; GitHub Actions access |
| V25 script coverage | Remaining triage reads return Cloud Guard 404 / Support 403; supply four missing prerequisites and resolve two no-data metric checks. Corrected helper defects have fresh passing evidence | Skill maintainers and OCI operator |
| V27 host task evaluation | Run the qualifying host evaluation with recorded host/model versions, run IDs and ≥0.8 task score | Evaluation maintainers; supported evaluator access |
| V28 behavioral comparison | Same prompts and budgets across four arms; publish task completion, generated-command validity and safety outcomes | Evaluation maintainers; controlled test environment |

## Environment-dependent validation

Instance/resource principals need suitable workloads; database, OKE and pipeline
sequences need provisioned test resources; cross-region behavior needs a second
region; PowerShell needs a Windows test host. A PAYG test tenancy may be needed
for some workloads. Each requires its own bounded test plan, spending limits and
authorization. Repository validation remains read-only; mutation recipes stay
shape-only until a separate lifecycle test is designed and authorized.

## Coverage beyond the current pack

The [audit](audit.md#unowned-services) identifies 11 unowned CLI groups covering
258 leaves. Dedicated Region, C3, Roving Edge, Alloy, media and IoT currently have
navigation guidance rather than dedicated operational skills. Identity-domain
federation and some fleet/database chains need deeper validation. CLI ownership
does not imply complete coverage of every Oracle product or certification.

Research should target these named gaps or a demonstrated user workflow. A useful
addition includes discriminating triggers, authoritative source provenance,
bounded examples and reproducible evidence; more files alone are not progress.
