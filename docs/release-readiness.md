# Release readiness — September 10, 2026

The current semantic-selection and component CI passes. Public-release readiness
also needs evidence about maintenance, live prerequisites, host task completion
and history hygiene. Those scopes remain separate from a green push workflow.

## Maintenance workflow

Manual runs now default to a preview that records the proposed notification and
never publishes an issue. Scheduled runs retain the intended notification path;
manual publication requires the explicit boolean input. GitHub documents these
[typed manual inputs](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)
and [workflow concurrency](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax).

The workflow serializes runs, tests notification behavior before inspecting CLI
versions and uploads the pinned/current versions, diff and notification outcome.
The notification helper reuses an exact-title open issue; a failed, malformed or
truncated issue search cannot become permission to create a duplicate. Large
bodies are bounded and link to the full artifact. Unit tests exercise creation
and repeated runs with a mock client, without sending GitHub messages.

```bash
gh workflow run cli-drift.yml --ref main -f publish_issue=false
```

A hosted manual preview can verify installation, comparison, artifact upload and
notification planning. It does not prove that the Tuesday cron fired or that an
actual issue was created. V24 retains that distinction.

See the [scoped sweep](evidence/validation-scripts.json),
[prerequisite diagnostics](evidence/prerequisite-diagnostics.json) and
[host recheck](evidence/host-recheck.json) for dated outcomes.

The [hosted preview](evidence/hosted-drift.json) completed successfully on commit
`8eb3d57`: OCI CLI 3.91.0 versus 3.92.1. The [captured diff](evidence/cli-drift.diff)
and [path impact analysis](evidence/cli-drift-impact.json) identify 35 added paths,
six removed paths and three relaxed required-flag sets. None of the removed or
changed paths appears in the authored OCI fences under skills/shared references.
This is not a full compatibility test of optional flags, callbacks or OCI services.
The notification outcome was `would-create`, with `published: false`. The package
continues to validate against its pinned CLI 3.91.0.

## Live prerequisites

A bounded probe in the selected profile's tenancy-root compartment and region
found an accessible Object Storage namespace and bucket. Multipart inspection
succeeded with an empty upload sample. The previous helper sweep incorrectly
left these prerequisites unresolved. The runner now discovers them through the
same read-only wrapper and never retains their values in its report. Missing or
failed discovery remains blocked; inherited values cannot change the scope.

Bastion, DevOps projects and Functions applications returned empty samples in that
same scope. Compute-agent CPU metric discovery was empty, and the validator still
reported no datapoints. These observations do not prove absence elsewhere in the
tenancy. No broader compartment scan or resource provisioning was performed.

Cloud Guard configuration lookup returned 404, so its enabled state and reporting
region could not be established. Oracle documents reporting-region mismatches as
one possible cause of this error; 404 alone does not establish that cause or a
missing resource. [Cloud Guard troubleshooting](https://docs.oracle.com/en-us/iaas/Content/cloud-guard/using/trouble.htm).

The dated triage evidence also contains Support 403. Oracle requires support
account setup and describes eligibility restrictions. Neither eligibility nor
missing IAM permission can be inferred solely from that status. An additional
user-validation probe was refused by the repository's conservative read-only
policy and made no service call; the policy was not weakened to bypass it.
[Listing support requests and prerequisites](https://docs.oracle.com/en-us/iaas/Content/GSG/support/list-incidents.htm).

## Native host and comparison

The installed host again rejected a single-case `claude plugin eval` attempt with
an early-access restriction. The check used no tool grants, no scaffold, mocks,
absent OCI configuration and no report publication. No task result was produced.

V27 therefore has no qualifying native-host task score. V28 still needs the same
controlled tasks and budgets across four arms, with task outcomes and generated
commands observed. The recorded semantic classifier is useful component evidence
but cannot supply those missing behavioral measurements. A new reviewed holdout
also remains necessary for a generalization claim.

## History preparation

The history scanner identifies two email occurrences in one historical JSON
blob, appearing in both its addition and removal patches. Current files pass the
source scan. Commit identities and author trailers are outside this scan's scope.

Preparation uses a separate mirror, a blob-specific replacement and the
[git-filter-repo](https://github.com/newren/git-filter-repo) tool. Acceptance for
the candidate is zero findings in reachable textual patch bodies, unchanged
current source tree and valid Git object connectivity. The original repository
and remote history remain intact during preparation.

Applying a candidate would replace published commit IDs. Review the candidate,
its source revision and the other active work before authorizing a remote
history replacement. Ordinary commits cannot remove material from old patches.
