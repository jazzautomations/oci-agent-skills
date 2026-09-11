# Service prerequisites and FinOps coverage — September 11, 2026

The [fresh scoped reads](evidence/service-prerequisites-2026-09-11.json) establish
current prerequisite state, not full workload validation:

| Read | Observation |
|---|---|
| Region subscriptions | The selected region is the home region |
| Cloud Guard configuration | DISABLED |
| Support incident list | HTTP 403, with selected user and home region supplied |
| Selected profile user | Email present and verified; no domain field in this response |
| Budget list | Empty bounded response |
| Cost-tracking tag list | One observed tag; values not published |
| Settled regional/root-compartment cost | Empty bounded response for the 30-day window ending two days ago |

An empty settled window is not proof of zero spend. Absence of a domain field is
not proof of the default domain. Verified IAM email does not prove that the user
has a provisioned Support account or Support user-group privileges. No registration,
IAM, service activation, infrastructure, account upgrade or support-ticket write
was performed. The seven reads made no model calls.

## Repository defect repaired

FinOps previously unconditionally inserted a regional boundary into
`coverage_gaps`. The script validation harness treats every such gap as nonpassing;
therefore even fully supplied regional inputs could never pass that scoped check.
The boundary is now retained in JSON `scope_limitations` and Markdown's scope
section. Actual coverage gaps remain blocking, and `complete` remains false:
the script does not certify the whole estate or promise aggregate savings.

The repair also closes false-clean paths: D15 now reports insufficient evidence
when no settled cost series exists or an observed service/currency has fewer than
eight days; D16 reports a missing month/currency forecast; D17 reports missing
positive currency-qualified spend. Supplying a budget or tag cannot convert empty
source data into a clean result. Detector thresholds and savings rules are unchanged.

Synthetic regressions prove that a fully supplied scoped case can pass while a
real missing-data condition still cannot. The full suite passed **582 tests with
three warnings in 44.03 seconds**; 22 FinOps tests passed. This is not a new live
full-scan result, and does not change V25 to PASS. The `skill-creator` review kept
the repair scoped to evidence semantics rather than adding deployment authority.
Its generic validator still rejects the existing `compatibility` metadata;
repository format and size validation support that field.

The full offline release recheck also passed 582 tests (101.83 seconds in the
parallel gate run) and retains 24 PASS, two PARTIAL, one FAIL and one UNMEASURED.
Its nonzero exit is expected for the four existing release blockers; no new host
inference or full live sweep was requested by that recheck.

## Support diagnosis and next account step

The Support reference no longer equates 403 with lack of entitlement, or 401 with
an unsubscribed region. These historical HTTP responses cannot establish those
causes by themselves. Oracle documents Support onboarding, identity association,
Support user groups and IAM as separate prerequisites. See
[Support account configuration](https://docs.oracle.com/en-us/iaas/Content/GSG/Tasks/usingsupport.htm)
and [user validation](https://docs.oracle.com/en-us/iaas/Content/GSG/support/validate-user.htm).

The next account action is to inspect the authenticated Console's Support flow
and resolve any onboarding or user-group/identity binding issue it actually shows.
The current reads cannot establish which of those is missing. Registration,
privilege changes and Cloud Guard activation are account mutations, outside the
repository's read-only validation contract. They require a separately scoped
account-change workflow; repeating tests or changing scores cannot substitute.

V24 still needs an actual scheduled event; V27 needs new full behavioral evidence;
V28 needs the native four-product comparison. Fresh paid model evaluations remain
paused and the original $20 aggregate ceiling has not been renewed.
