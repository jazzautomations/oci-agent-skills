Purpose: answer "does OCI have X / which CLI do I use" with evidence instead of a guess — four probes, in cost order, and the five answer classes each one can produce.
Source: research/09c §A8, research/16 §C.2, research/A1 §7-8, live reads in this tenancy; generated 2026-09-08; verified-on CLI 3.91.0

## 1. The four probes, cheapest first

**P1 — the offline leaf catalog.** No credentials, no network, bounded to 400 bytes. Answers
"is there a CLI path for this intent, and what does it require".

```bash
python3 scripts/catalog.py find "list instances" --read-only
python3 scripts/catalog.py required "compute instance list" --json
python3 scripts/catalog.py query --service marketplace --fields name,ops,read_only --json
```

A miss exits 1 with suggestions. A hit proves the *command* exists in CLI 3.91.0 — it proves
nothing about entitlement, region availability or your policy.

**P2 — the service is offered to this tenancy.** `limits service list` returns the programmatic
service names the limits service knows for this tenancy; it is the cheapest live "is this
product a thing here" signal.

```bash
oci limits service list --compartment-id ${TENANCY_ID} --limit 100 --query "data[].name" --output json
```

Caveat that bites: a *removed CLI group* can still appear here. `ai-anomaly-detection` is listed
even though the group went away in 3.65. Read it as "the service name is known", not "you can
drive it from the CLI".

**P3 — the tenancy actually has some.** Resource Search answers "do instances of it exist",
across compartments, in one call.

```bash
oci search resource structured-search --query-text "query all resources where compartmentId = '${COMPARTMENT_ID}'" --limit 50 --query "data.\"items\"[].\"resource-type\"" --output json
```

Search covers indexed resource types only; an empty result is "none indexed here", never
"the service does not exist".

**P4 — the owning group answers.** Call the product's own `list` with `--limit`. This is the
only probe that distinguishes entitlement from absence, and it is the one that costs an API call.

```bash
oci marketplace listing list --limit 20 --query "data[].{name:name,type:\"listing-type\"}" --output json
```

## 2. The five answer classes

1. **Core OCI, owned by a sibling skill.** Name the skill and stop. Do not emit its commands.
2. **OCI, envelope only.** The CLI sizes the instance; the business objects need the product's
   REST API. Say which half the user is asking about before routing.
3. **OCI, but this group has no dedicated skill** (`iot`, `media-services`, `ocvs`, `desktops`,
   `mngdmac`, `ccc`, `rover`). Give the group root and the docs URL; that is the whole answer.
4. **Oracle, not OCI.** Fusion SaaS, NetSuite, Oracle Health, compliance attestations. Hand off
   by name to the console or API that owns it; emit no `oci` command.
5. **No control plane at all.** GraalVM, Helidon, Micronaut, Coherence, Dedicated Region ids.
   Say so plainly.

## 3. Realm and region come before all four

`iam region list` is **realm-scoped**: 44 rows live in this tenancy, against 46 in the SDK's oc1
table and 85 known regions overall. It answers "regions my tenancy could subscribe to", never
"regions Oracle operates". Endpoints are templated on the realm's second-level domain, so never
string-build one — pass `--region` and let the SDK resolve it.

## 4. What a routing answer must contain

Owner (skill, product REST API, or console) · the exact `oci <group> <noun>` root or the named
API · one sentence on why it is not the neighbouring product · the evidence class (P1-P4) that
backs it. If the evidence is P1 only, say "the command exists; entitlement unverified".

Docs (HTTP 200, 2026-09-08): https://docs.oracle.com/en-us/iaas/Content/General/Concepts/regions.htm ·
https://docs.oracle.com/en-us/iaas/Content/Search/Concepts/queryoverview.htm
