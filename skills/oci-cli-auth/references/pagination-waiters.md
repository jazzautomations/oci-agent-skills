Purpose: get a complete list back, and know whether a `--wait-for-state` that never returns is stuck or merely slow.
Source: research/04a-cli-auth-ergonomics.md §2.3, §2.5, §2.13, research/10a-sdk-developer-patterns.md §2.7–2.8; generated 2026-09-09; verified-on CLI 3.91.0.

## Contents
1. Completeness — `--all`, `--limit`, `--page`
2. Auditing a sweep for silent truncation
3. Waiters and work requests
4. Audit events, the paging worst case

## 1. Completeness

| Flag | Behaviour |
|---|---|
| `--all` | auto-paginates; **mutually exclusive with `--limit`** — `UsageError: If you provide the --all option you cannot provide the --limit option` [verified live 2026-09-09] |
| `--limit N` | one bounded page |
| `--page-size N` | tunes the per-call page; valid only with `--all` or `--limit`, ignored otherwise [verified] |
| `--page <token>` | manual paging from the previous call's `opc-next-page` header [verified] |
| `--stream-output` | prints as it fetches; works **only** with `--all` — use it for audit and log dumps so the CLI does not buffer everything [verified] |
| `--skip-deserialization` | faster on large pages, but **keeps camelCase keys**, changing every `--query` path [verified] |

Coverage in 3.91.0: **1,930 of 9,145 leaf commands expose `--all`, 2,084 expose `--limit`**
[computed from `research/data/cli-tree.json`]. So `--all` is not always available; when it
is not, page manually on `opc-next-page` rather than accepting the first page.

## 2. Silent truncation

Without `--all`, the CLI writes to **stderr**:

```
WARNING: This operation supports pagination and not all resources were returned.
Re-run using the --all option to auto paginate and list all resources.
```

[verified live 2026-09-09 on `limits value list --limit 5` and `work-requests
work-request list --limit 5`]. Exit status stays 0 and stdout is valid JSON, so an agent
capturing stdout only reports a short list as if it were the whole answer.

Rules:
- If the leaf has `--all`, pass it. Confirm with `scripts/catalog.py help "<leaf>"`.
- Never discard stderr. `list_all.sh` keeps it and reports the warning as a finding.
- The read-only wrapper injects `--limit 100` when a leaf supports it and no bound was
  given, and refuses `--all` unless `OCI_RO_ALLOW_ALL=1` — a bounded read by default, so
  treat every wrapper result as possibly partial until you widen it deliberately.
- A count taken from a bounded page is a floor, never a total. Say which it is.

## 3. Waiters and work requests

- 3,935 of 9,145 leaves accept `--wait-for-state`, with `--max-wait-seconds` and
  `--wait-interval-seconds` [computed; flags verified].
- **Accepted states differ per command — read them from `--help`, never hard-code.** Two
  vocabularies share the flag: `compute instance launch` takes resource states
  (`PROVISIONING|RUNNING|…`) while `compute instance terminate` takes *work-request*
  states (`ACCEPTED|IN_PROGRESS|FAILED|SUCCEEDED`) [verified].
- Exit codes: "If timeout is reached, a return code of **2** is returned. For any other
  error, **1**" [verified]. rc=2 means the work may still be running — do not re-issue the
  operation; go look at the work request. rc=1 is a real failure.
- Generic browsing (Compute family; many services ship their own namespace such as
  `oci ce work-request`) [verified live 2026-09-09, returned `LaunchInstance/ACCEPTED`]:

```bash
oci work-requests work-request list --compartment-id "$C" --all \
  --query 'data[].{op:"operation-type",status:status,pct:"percent-complete",id:id}'
```

Then `work-request-error list --work-request-id "$WR" --all` for why it failed, and
`work-request-log-entry list --work-request-id "$WR" --all` for how far it got. A request
sitting at `ACCEPTED` with `percent-complete: 0` is queued, not failed.

## 4. Audit events

`audit event list` is the worst paging case: per compartment **and** per region, no
tenancy-wide sweep, 365-day retention. Iterate `iam compartment list
--compartment-id-in-subtree true --all` across subscribed regions, and always pass `--all
--stream-output`.

Two traps [both verified live 2026-09-09]:
- `event-name` and `identity."principal-name"` are nested inside each item's `data`
  object; only `event-time` is top-level. Project
  `data[].{t:"event-time",op:data."event-name",who:data.identity."principal-name"}`.
- The help states that seconds and milliseconds in `--start-time`/`--end-time` must be 0.
  A call with `:30` seconds was nonetheless accepted and returned rows on 2026-09-09
  [unverified — the documented constraint was not reproducible here; keep sending
  minute-granular times].

## Links
[Pagination](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/usingapi.htm) ·
[Work requests](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/workrequests.htm) ·
[Audit](https://docs.oracle.com/en-us/iaas/Content/Audit/Concepts/auditoverview.htm) (200, 2026-09-08)
