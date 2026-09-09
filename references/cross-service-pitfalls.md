Purpose: the nine failure modes that bite in every OCI service — read before the first `list`, `get` or write of any skill.
Source: research/04c-core-services-pitfalls.md (§ Cross-service pitfalls); generated 2026-09-08; verified-on CLI 3.91.0

## Contents
1. The nine — symptom to correct move
2. Scoping: compartment, availability domain, region
3. Writes: work requests and replace-all `update`
4. Reads: paging, limits vs capacity
5. Secret hygiene

## 1. The nine — symptom to correct move

| # | Pitfall | What you see | Correct move |
|---|---|---|---|
| 1 | `-c/--compartment-id` is required and never inherited | "resource not found", or an empty list | Pass the exact compartment (tenancy OCID only if you mean root); sub-compartments are excluded unless the op has `--compartment-id-in-subtree true` |
| 2 | AD-scoped vs regional resources | Empty list, **not** an error | Pass `--availability-domain` only where the resource is AD-scoped (§2) |
| 3 | Every OCID embeds region and tenancy | 404 `NotAuthorizedOrNotFound` | Never copy an OCID between regions; re-resolve it by name in the target region |
| 4 | `NotAuthorizedOrNotFound` means one of three things | Same 404 for all three | Wrong compartment / missing policy / genuinely deleted — check `oci iam policy list -c <root>` before assuming it is gone |
| 5 | Async ops return work requests | The create response `id` is not the resource | Prefer `--wait-for-state`; raise `--max-wait-seconds` for LB and OKE (§3) |
| 6 | `update` verbs replace whole collections | Rules or exports you did not touch disappear | Read → merge → write, or use the incremental verbs (§3) |
| 7 | Pagination is off by default | Inventory silently truncated at 50 or 100; a WARNING on stderr scripts discard | `--all` for audits, `--limit` for interactive checks |
| 8 | Service limits, not the API, decide what you can create | A launch that "should" work fails | Query limits and availability first (§4) |
| 9 | Secret material must never be persisted | PAR access-uri, secret bundles, session keys in a log or commit | Redact before writing anything down (§5) |

## 2. Scoping: compartment, availability domain, region

| Scope | Resources |
|---|---|
| AD-scoped | Instances, block and boot volumes, FSS file systems, mount targets |
| Regional | VCNs, subnets (regional by default since 2018), buckets, vaults, load balancers |

- Subtree listing exists only on some ops (Monitoring, Search, some `list`s): `--compartment-id-in-subtree true`.
- Cross-compartment discovery, one call [verified]:
  `oci search resource structured-search --query-text "query instance resources where displayName =~ 'web'"`
- A 404 after a region switch is pitfall 3, not a permissions problem — check the OCID's region segment (`ocid1.instance.oc1.<region>....`) first.

## 3. Writes: work requests and replace-all `update`

| Concern | Services | Handling |
|---|---|---|
| Async / work request | LB, API Gateway, Bastion, Container Instances, OKE, FSS replication, Object Storage replication | Use `--wait-for-state`; the CLI polls the work request for you. `oci lb work-request get --work-request-id "$WR"` [verified] |
| Whole-object write | Route rules, security-list rules, FSS export options, NSG id lists, lifecycle policies, API Gateway specs, instance metadata | Read → merge → write |
| Genuinely incremental | NSG rules | `oci network nsg rules add` / `update` / `remove` |

Treat every `update` as destructive to the collection it names until proven otherwise, and show the merged payload before running it.

## 4. Reads: paging, limits vs capacity

- `--all` on any `list` that feeds an inventory or an audit; `--limit` when a human is reading the output.
- Before a launch that "should" work [verified]:

```bash
oci limits value list --compartment-id "$TENANCY" --service-name compute --limit 10
oci limits resource-availability get --service-name compute \
  --limit-name standard-a1-core-count \
  --compartment-id "$TENANCY" --availability-domain "$AD"
```

A limit above zero still is not capacity: out-of-host-capacity is a separate failure, triaged by the limits/capacity skill.

## 5. Secret hygiene

Never let these reach a research file, a log, a transcript or a commit: PAR `access-uri`, secret bundle contents, bastion session private keys, API signing keys, full tenancy and compartment OCIDs. Redact as `ocid1...redacted`. Full rules: `references/redaction.md`.

## Docs (HTTP 200, checked 2026-09-08)

- Compartments: https://docs.oracle.com/en-us/iaas/Content/Identity/compartments/managingcompartments.htm
- Regions and availability domains: https://docs.oracle.com/en-us/iaas/Content/General/Concepts/regions.htm
- Service limits: https://docs.oracle.com/en-us/iaas/Content/General/service-limits/default.htm
- Search query syntax: https://docs.oracle.com/en-us/iaas/Content/Search/Concepts/queryoverview.htm
