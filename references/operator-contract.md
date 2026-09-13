# Operator contract
Purpose: shared scope, reads, changes, evidence, host hand-off and CLI cadence.
Source: research/A1 (docs/operations.md), research/12 §C, research/16 §E.3; generated 2026-09-08; verified-on CLI 3.91.0.

## 1. Establish the target

Resolve profile (or workload identity), tenancy, region and compartment **before the
first call**; never fall back to `DEFAULT`.

| Rule | Why |
|---|---|
| After an error, never substitute the root compartment, home region, another profile or a broader principal | the retry answers a different question |
| Region subscription, IAM grant, service limit and capacity are **four different facts** | each fails differently |
| Say whether a read was subtree-wide (`--compartment-id-in-subtree true`) | it decides whether you see one compartment or the tenancy |

Identity Domains use the domain `--endpoint`, not the regional IAM one (`auth-modes.md`
for `--auth` and principal detection). IAM is the boundary; this contract and the guard
are advisory.

## 2. Bounded reads

- Explicit compartment and region, short time window, small page, `--query` + `--limit`.
- A next-page token or pagination warning means the inventory is **incomplete**: say so,
  and name compartments you could not read.
- Empty result = wrong scope | missing permission | indexing delay | genuinely none;
  never collapse the four into "none found" (`error-triage.md`).
- Most operations have **no `--dry-run`**, and a JSON skeleton is not one: describe the
  request and its effects, never fake a simulation.

## 3. Changes and recovery

Respect host permissions and the requested response format, including blocked
outcomes. Do not add excluded commands or unrequested discovery. Read examples
are optional diagnostics. Existing authorization covers its agreed scope only.

| Phase | Requirement |
|---|---|
| Before | Target, current state, intended diff, cost/downtime, verification, rollback — or "NONE, irreversible" |
| Authorization | Covers the agreed operation only, never another target or a destructive replacement; destruction needs confirmation of the exact resources and data loss |
| Conditional write | Pass the ETag (`--if-match`) where supported |
| Terraform | Review binds to the saved plan's exact bytes; a re-plan invalidates it; plan and state are secrets |
| Ambiguous write | Never retry blindly: inspect the work request and resource state; reuse the idempotency token |
| Polling | Bound it; separate acceptance, readiness and app health |
| Rollback | Must cover irreversible data/schema change, not just infrastructure |

## 4. Evidence and confidentiality

Report scope, observation time, CLI version, truncation and verification status. Keep
doc review, command-shape validation, live read and deployment test apart: a tool name or an HTTP 200 never proves a working app or a complete
inventory. Names, OCIDs and tenancy structure are private data (`redaction.md`).

## 5. Cloud Shell and Code Editor

| Fact | Consequence |
|---|---|
| VM is service-owned, not in your tenancy `[doc]` | no dynamic group; instance principal unusable |
| CLI pre-authenticated to the Console region at session start `[doc]` | switching region does not re-point a live session |
| 5 GB home (home region), 24 h max, 60 min idle, UTC, no inbound IP `[doc]` | wrong host for long or listening jobs |
| Reaches only home-region resources unless Public Network is on `[doc]` | egress failure is policy, not outage |
| Support Management is unsupported there `[doc]` | a 4xx means "use a local CLI", not "you lack access" |
| Code Editor shares its IAM policies and home dir `[doc]` | plugins also need `inspect compartments in tenancy` |
| No launch API; a `/cloudshell` literal exists `[verified]`, unconfirmed | hand off with a Console deep link (`console-links.md`) + Developer tools menu |

## 6. CLI pin and re-verification cadence

Pin the CLI version in every skill; an unpinned example is undated evidence. Releases
are weekly and the surface grows ~1 %/quarter `[verified]`.

| Trigger | Action |
|---|---|
| `3.x.0` bump (~monthly) | re-extract and diff the `oci --help` tree; re-run `check_examples.py` |
| Weekly release | grep the new CHANGELOG section for `[BREAKING]` and for `oci <group>` literals used in `catalog/examples.json` |
| Quarterly | live-safe subset (`--limit 1`) on a real tenancy; refresh leaf/region data |
| `[BREAKING]` on a shipped path | patch the skill in the PR that bumps the pin |

Search `[BREAKING]`: required-flag changes can break examples even when paths
remain unchanged. Removed command groups also require updates.

## Links (HTTP 200, 2026-09-08)

- https://docs.oracle.com/en-us/iaas/Content/API/Concepts/cloudshellintro.htm
- https://docs.oracle.com/en-us/iaas/Content/API/Concepts/code_editor_intro.htm
