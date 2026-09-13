# Structured host evaluation and scope repairs — September 13, 2026

The capacity helper previously read tenancy-wide headroom even when the task
concerned a child compartment. It now requires an explicit `COMPARTMENT_ID`, uses
the tenancy for limit metadata, and queries quota/usage headroom in the target
compartment. It resolves the exact limit's scope before adding an availability
domain: AD is required for AD-scoped limits and omitted for regional/global limits.
Missing, ambiguous or truncated scope metadata stops further reads.

The helper keeps the shared read-only wrapper and returns one JSON report with
configured values, compartment headroom and `physical_capacity_verified: false`.
Existing callers must supply `COMPARTMENT_ID`; selecting the tenancy itself is
still possible by explicitly supplying the same target. It never launches a
resource to test availability.

The skill and reference now distinguish limits, quotas, budgets, shape listings
and physical capacity. Existing-instance shapes cannot extend a scoped shape
listing. They also remove unsupported promises about paid upgrades, GPU timing,
quota-policy location and immediate policy propagation. Support 401/403/404
responses retain their diagnostic ambiguity. These are documentation and offline
corrections, not new live service evidence. Primary references include Oracle's
[headroom API](https://docs.oracle.com/en-us/iaas/tools/oci-cli/latest/oci_cli_docs/cmdref/limits/resource-availability/get.html),
[quota overview](https://docs.oracle.com/en-us/iaas/Content/Quotas/Concepts/resourcequotas.htm)
and [capacity troubleshooting](https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/troubleshooting-out-of-host-capacity.htm).

Eleven skills pointed to a nonexistent local `scripts/whoami.sh`. Their scope
guidance now links the actual shared helper and permits an available scoped host
tool. Auth guidance and the authoring stencil no longer assume every host can
execute a script. Document review and command drafting remain distinct from live
identity verification. Four edited entrypoints use the existing concise
untrusted-output contract to stay within the unchanged context budgets.

## Validation

The 12 new regression tests cover compartment targeting, AD/regional/global
dispatch, missing or ambiguous metadata, missing target scope and failed headroom.
All **625 test cases have passing coverage**: the full local attempt passed 624
and failed the copy-installation case with `ENOSPC`; that exact case then passed
separately with its temporary copy in RAM. Earlier disk-related failures remain
recorded. Hardlinks and disabled bytecode writes reduced disposable environment
storage; no test assertion or threshold was relaxed.

All 28 strict CI validator commands passed, with failed storage-constrained
attempts retained and the affected checks rerun. The updated script policy and
generated registry were checked again after the final helper change. The generic
skill-creator validator does not accept this repository's `compatibility` field;
the repository's strict frontmatter and portability checks pass with it preserved.

## Model evidence

The historical Claude four-reference experiment was reverified at its immutable
revision: pack 39/40, adibirzu reference 33/40, Oracle reference 38/40 and bare
baseline 38/40. A separate native checked experiment remains 35/40 versus 38/40.
These protocols are different, and their scores do not certify changed sources.
The public adibirzu and Oracle MCP heads still match the compared revisions.

The native OpenCode adapter now uses JSON-schema output, the installed API's
`info.structured` field, and independent JSON Schema validation. Two local
deterministic tests accept valid output and reject a wrong type. The host's
message-list export returned HTTP 400 after model responses; the collector now
reads its isolated native transcript database in read-only mode. The earlier
failures remain preserved.

A diagnostic cohort using `opencode/mimo-v2.5-free` retained eight attempts over
four tasks: native 3/4 and baseline 0/4. It was stopped to repair the independently
confirmed scope defects before a full comparison. Both arms wrongly extended a
shape listing with a shape from an existing instance. A later native T08 probe
passed without activating a skill; it cannot establish a causal improvement.
A subsequent explicit-StructuredOutput preflight passed T02 in both arms, also
without native activation. Full comparative results require a separate report.

Only authorized package documents and synthetic observations were sent to the
free provider; no generated OCI command executed and no paid fallback was used.
[Zen's terms](https://opencode.ai/docs/zen/#privacy) permit model-improvement use
of MiMo free-tier content. Raw model records remain private; the
[sanitized evidence](evidence/structured-host-repairs-2026-09-13.json) records
grades, protocol limits, hashes and verification results.

This follow-up does not waive V24, V25, V27 or V28, and does not claim overall
superiority or a completed native four-product comparison.
