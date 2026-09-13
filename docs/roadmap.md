# Roadmap and release criteria

Latest: [semantic regressions and trial reads](semantic-validation-2026-09-13.md)
support the public preview; the four stable-release gates remain open.

The v2 skill set ships as package **0.2.1 preview**. The next release requires
closing the [validation matrix](validation-matrix.md), not merely renaming the
version or increasing the skill count. All current evidence is scoped and dated.

| Work | Acceptance evidence | Owner / prerequisite |
|---|---|---|
| V24 hosted drift | Capture a successful actual scheduled run; manual issue publication and duplicate handling already have evidence | CI maintainers; active Tuesday GitHub Actions schedule |
| V25 script coverage | Resolve disabled Cloud Guard and Support 403, then collect successful scoped reads and sufficient settled cost/forecast/budget evidence | Skill maintainers and OCI operator; service access and real billing history |
| V27 host task evaluation | Repeat all 40 tasks on current skills with recorded host/model versions and ≥0.8 task score; preserve exact-answer failures and distinguish fixture evidence from complete task semantics | Evaluation maintainers; explicit model budget and supported evaluation method |
| V28 behavioral comparison | Deploy the native alternatives with the same prompts and budgets; publish task completion, generated-command validity and safety outcomes | Evaluation maintainers; controlled test environment and bounded budget |

V22 is closed: published-history cleanup and the current-file/full-history scans
pass. See the [latest follow-up](validation-closeout-2026-09-13.md) for dated
verification and the remaining four gates.

V19/V20 pass on the recorded semantic-description selections in the
[release matrix](validation-matrix.md). Relevant input changes invalidate this
evidence. The [investigation](semantic-routing.md) covers blind
inputs, scope repairs, failed development trials and remaining generalization gaps.

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
