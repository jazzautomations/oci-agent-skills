Purpose: the renamed, removed, nested and colliding OCI names that turn a correct intent into `No such command` or into an answer about a different product.
Source: research/09c §A5/A8, research/11 §15, research/16 §A.5/§C.1, research/14 §6; generated 2026-09-08; verified-on CLI 3.91.0

## 1. Removed from the CLI — the group is gone, the concept may not be

| You will type | Reality |
|---|---|
| `oci anomaly-detection` | **removed in CLI 3.65**. `ai-anomaly-detection` is still a *limits* service name, so `limits service list` still shows it — that is not a live CLI group |
| `oci os-management` | removed in 3.65; the survivor is `oci os-management-hub` (different nouns, different agent) |
| `oci data-transfer`, `oci service-mesh` | removed; no replacement group |
| `oci compliance` | never existed. Compliance artifacts are Console-only (Identity & Security -> Compliance) |
| `oci kms vault list` | does not exist — Vault listing lives elsewhere; route to `oci-vault-certificates` |

## 2. Nested where you expect a top-level group

- `oci ai language batch-detect-*` — a **two-level** group. `oci ai-language` is not a command.
  Vision, Speech and Document Understanding are the flat ones (`ai-vision`, `speech`, `ai-document`).
- `oci mysql db-system heatwave-cluster` — the HeatWave accelerator hangs off the DB system.
  There is **no** `oci mysql heat-wave-cluster`. Live on 3.91.0 that typo returns
  `Error: No such command 'heat-wave-cluster'.` with **no** "Did you mean" list [live 2026-09-09].
- `oci compute compute-capacity-report` — not `capacity-report`; and `--compartment-id` must be
  the **root** compartment.

## 3. Same word, different product

| Word | The two meanings |
|---|---|
| anomaly detection | removed AI service (sensor data) vs `oci costad` cost anomaly monitors (spend) |
| compliance | Oracle's own attestations (SOC/PCI, Console-only) vs `oci fleet-apps-management` *patch* compliance — the Python SDK's `list_compliance_records` / `generate_compliance_report` are the **fleet** ones |
| multicloud | `oci multicloud` (anchors, subscriptions) vs `oci dbmulticloud` (keys, blob mounts) — the split *is* the routing decision for Database@Azure/AWS/GCP |
| capacity | `oci limits` / `oci quotas` (what you may create) vs `oci capacity-management` (an OCC enterprise contract) vs `compute-capacity-report` (does the hardware exist right now) |
| WebLogic | WLS for OCI (a Marketplace stack) vs WebLogic Management Service (`oci wlms`) — two products |
| region | realm-scoped `iam region list` (44 live here) vs `iam region-subscription list` (what you are subscribed to) vs the SDK's 85 known regions |
| email | the CLI group is `oci email`; the **limits** service name is `email-delivery` — `--service-name email` returns 400 `InvalidParameter` [live 2026-09-09] |

## 4. "It has no control plane" is a real answer

GraalVM, Helidon, Micronaut, Coherence, NetSuite and Oracle Health have **no OCI CLI group**.
So does Dedicated Region: it is a region id, used through `--region`/`--endpoint`, and its id and
key are "not available in public documentation". Saying so is the correct answer; inventing
`oci graalvm` or `oci netsuite` is not.

## 5. Do not read absence as absence

- A missing MCP wrapper does not mean the product lacks an API.
- An SDK method does not prove entitlement, or availability in this region or realm.
- Gov and sovereign realms carry an *authorized-services subset*: a DNS failure or
  `ServiceNotFound` there is a legitimate "not offered here", not something to retry.
- A `NotAuthorizedOrNotFound` on a product list is ambiguous by design — missing resource, or
  missing policy, or wrong region, or wrong compartment. It is not proof the service is absent.

## 6. When the name is simply wrong

`Error: No such command '<x>'.` is a **local** failure: nothing left the host, so never retry it.
Trust the suggestion list when the CLI prints one; when it does not, resolve the real leaf with
`python3 scripts/catalog.py find "<intent>" --read-only` rather than guessing a second spelling.

Docs (HTTP 200, 2026-09-08): https://docs.oracle.com/en-us/iaas/Content/API/References/apierrors.htm ·
https://docs.oracle.com/en-us/iaas/tools/oci-cli/latest/oci_cli_docs/
