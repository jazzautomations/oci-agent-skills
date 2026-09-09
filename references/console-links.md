Purpose: build an OCI Console deep link that resolves — the host rule, route segments proven from the live bundle, and the convention-only detail patterns.
Source: research/12-support-limits-console-deeplinks.md (B1–B5); generated 2026-09-08; verified-on CLI 3.91.0

## 1. Host rule

Emit `https://cloud.oracle.com/<path>?region=<region-id>`. Region is a **query parameter**, never
a hostname prefix. **Never construct `console.<region>.oraclecloud.com`.**

| Host form | Behavior |
|---|---|
| `cloud.oracle.com/<path>?region=<r>` | the only form to emit [verified] |
| `console.<region>.oraclecloud.com`, older regions | 301 → `cloud.oracle.com/?region=<r>` (13 verified: us-ashburn-1, us-phoenix-1, eu-frankfurt-1, sa-saopaulo-1, ap-tokyo-1, …) |
| same, newer regions | **404** [verified]: us-chicago-1, ap-batam-1, mx-monterrey-1, eu-turin-1, af-casablanca-1, ap-singapore-2, il-jerusalem-1 |

`<region-id>` is the full identifier (`us-chicago-1`), not the airport code. Params real in the
bundle [verified]: `compartmentId`, `region`, `tenant`, `domain`, `startTime`/`endTime`. A link
with no `region` lands wherever the Console was last used — warn, never guess.

## 2. A 200 proves nothing

The Console is a client-side-routed SPA: every path returns the same app shell.
`/compute/instances?region=us-chicago-1` returned `200 len=22931`; so did
`/thisroutedoesnotexist-zzzz` and `/aaa/bbb/ccc/ddd`, differing only in the Akamai telemetry
blob [verified]. **Never validate a Console route with `curl -I`, and never cite a 200 as proof a deep
link works.** §3 comes from string literals in the Console's own JS bundle (plugin 4.23.5hotfix.1) [verified].

## 3. Verified route segments

Literals in the bundle [verified]; append `?region=<r>` (except identity, §5).

| Target | Path |
|---|---|
| Home | `/`, `/home`, `/dashboard` |
| Compute | `/compute/instances`, `/compute/instances/create`, `/compute/images` |
| Networking | `/networking/vcns`, `/networking/load-balancers/load-balancer`, `/networking/load-balancers/network-load-balancer` |
| Storage | `/object-storage/buckets`, `/block-storage/volumes` |
| Database | `/db/adb`, `/db/adb/adw`, `/db/adb/atp` |
| Containers | `/containers/clusters` |
| Observability | `/monitoring`, `/logging`, `/audit/events` |
| Cost | `/account-management/cost-analysis`, `/usage` |
| Limits | `/limits` |
| IAM | `/identity/policies`, `/identity/compartments`, `/identity/users` |
| Resource Manager | `/resourcemanager`, `/resourcemanager/quickstarts` |
| Search, Cloud Shell | `/search`, `/cloudshell` |
| Support | `/support`, `/support/list`, `/support/service-request/create`, `/support/limit-increases`, `/support/limit-increases/create-request` |

Parameterized routes are literals too (`/security/dedicated-kms/:id`, `/dashboard/group/:groupId`)
[verified] — the `<list-route>/<id>[/<tab>]` convention §4 extrapolates from.

## 4. Detail-page patterns — `[unverified]`

Per-service plugin bundles are lazy-loaded and no manifest is exposed unauthenticated (three
manifest paths 404 [verified]). These rows are **convention only** — caption them "confirm in
browser", never as fact.

| Resource | Pattern `[unverified]` |
|---|---|
| Instance | `/compute/instances/<instance-ocid>` |
| VCN, subnet | `/networking/vcns/<vcn-ocid>`, `…/<vcn-ocid>/subnets/<subnet-ocid>` |
| Bucket | `/object-storage/buckets/<namespace>/<bucket>/objects` (name-keyed; no OCID) |
| ADB | `/db/adb/<autonomousdatabase-ocid>` |
| OKE cluster | `/containers/clusters/<cluster-ocid>` |
| Alarm | `/monitoring/alarms/<alarm-ocid>` |
| RM stack | `/resourcemanager/stacks/<ormstack-ocid>` |
| Policy, compartment | `/identity/policies/<policy-ocid>`, `/identity/compartments/<compartment-ocid>` |
| Log search + query | `/logging/search` — **param shape unknown**, do not fabricate one |

## 5. `scripts/console_url.py` contract

Pure string work — no network, no auth. OCID grammar `ocid1.<type>.<realm>.<region>.<unique>`;
the region field is the **airport code** (`ord`, `iad`) and is **empty** for IAM resources.

- Region order: `--region` → airport code mapped via `research/data/regions.json`
  (`{"key":"ORD","name":"us-chicago-1"}`, 44 regions [verified]) → `OCI_CLI_REGION`/profile → omit + warn.
- Identity (`policy`, `compartment`, `user`, `group`, `tenancy`) is home-region scoped: no `region`.
- Buckets need `namespace` + `bucket`; subnets need the parent VCN OCID — fail loudly, never guess.
- Reject anything not starting `ocid1.`; raise on an unmapped type rather than invent a path.
- Params in fixed order `region`, `compartmentId`. Every §4 pattern returns `verified=False`.
