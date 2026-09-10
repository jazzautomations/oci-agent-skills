# OCI waste assessment

Run the [FinOps skill](../skills/oci-finops-waste/SKILL.md) with explicit region and compartments.
It joins attachment lists, checks metric coverage, compares native Cloud Advisor findings,
and reports governance gaps. Reads are capped by resource count and a total call budget.

The complementary checks include stopped-VM storage, early orphan candidates, multipart
uploads, reservations, missing budgets and coverage gaps. Native Advisor already covers
several utilization/lifecycle patterns; D18 corroborates rather than claiming novelty.

Price exposure uses public graduated bands and a dated snapshot. It is **not confirmed
savings**: eligibility, shared allowances, contractual rates and overlap need billing evidence.
No remediation executes. Read failures, missing metrics and saturated pages are explicit.

[Sample evidence](evidence/finops-sample-report.md) records exactly what ran live.
