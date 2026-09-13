# Semantic and trial validation — September 13, 2026

The current preview adds executable tests of authored query results and helper
workflows, plus bounded reads against the existing OCI trial account. No cloud
resources were created or changed, and no new model benchmark was run.

## Trial evidence

The [sanitized read report](evidence/trial-semantics-2026-09-13.json) records
**39 requests: 38 successful reads and one `LifecyclePolicyNotFound` 404**.
The latter establishes the service-reported absence of that bucket's lifecycle
policy; it is retained as an unsuccessful request, not successful policy data.
Reads used the shared read-only wrapper, the configured region, the tenancy root
and one observed active child compartment, with collection limits of ten.

**34 current authored-query replays passed; 16 used nonempty input.** Independent
Python field/filter expectations were compared with the actual CLI output.
These include compute, identity, network, storage and security-posture responses.
The initial 32 comparisons are retained; the final offline replay adds the two
captured security-list responses and uses current source hashes. It makes no
additional OCI calls. Saturated samples remain marked as bounded.

Eighteen empty-input comparisons validate only the empty behavior. They do not
establish nonempty OKE, Vault, monitoring or other unavailable resource behavior.
Private raw responses contain account data and are withheld. Public live evidence
is a sanitized collector attestation; its raw inputs cannot be independently
replayed from this repository. Offline synthetic tests are fully reproducible.

## Corrections protected by executable tests

- Cost projections preserve currency, time boundaries and complete tag rows.
- NSG output retains direction, source/destination types, protocol, port ranges,
  ICMP options and the stateless flag.
- Public security-list output includes IPv4 and IPv6 and retains full matching
  rules, allowing TCP ranges to be distinguished from UDP or unrestricted traffic.
- Node-pool output retains name, version and nested configured size, including null.
- Posture scans retain wrapper truncation flags even when a query returns fewer
  items than the page limit; incomplete reads cannot appear complete.

[Authored-query tests](../tests/test_authored_query_semantics.py) extract commands
from specific current source files and compare results against hand-authored
expectations. Where a pinned response contract exists, fixtures are also checked
against it. [Workflow tests](../tests/test_workflow_semantics.py) exercise bucket
list/detail classification, volume/attachment joins, pagination, failed reads,
audit windows and security findings using synthetic transport responses.

Run them without cloud credentials or model calls:

```bash
uv run --frozen --project runtime pytest -q tests/test_authored_query_semantics.py tests/test_workflow_semantics.py
```

These are component semantics, not a new execution of all 40 agent tasks. The
[original Luna comparison](luna-package-comparison-2026-09-13.md) is historical:
its scores and six command-field failures replay at immutable revision
`eba3fd3c9c306230842333ce48b58b82624f77e1`. Changed skills never inherit old scores.

## Validation result

The complete local suite passes **741 tests, nine dependency deprecation warnings,
63.83 seconds**, including copy-installation checks. All **31 strict CI commands**
also pass; the [validation receipt](evidence/semantic-checks-2026-09-13.json) records
the commands and results. The two semantic files
contribute 88 tests: 36 source-bound query fixtures and a separate null-node
configuration check, plus provenance/serialization checks and 14 workflow tests.

The repository frontmatter checks and both native Claude plugin validations pass.
The generic skill-creator quick validator rejects existing `compatibility` and
`paths` extensions; this is a validator-format mismatch, not a passing result.
Those supported repository fields were preserved.

## Preview scope

This work supports an explicitly labeled public preview, not stable-release
certification or a claim to outperform every OCI skills package. The full
[validation matrix](validation-matrix.md) still has four nonpassing gates:
Cloud Guard/Support and billing coverage, full current native task behavior,
native comparison across four deployed products, and observation of the scheduled drift trigger.
Services requiring additional account access remain deferred; publishing the
preview does not turn those gates green.
