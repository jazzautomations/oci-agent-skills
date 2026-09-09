Purpose: cite an Oracle Architecture Center design without guessing a URL — the URL grammar, the `pls/topic/lookup` resolver, the staleness rules, and the 25 architectures worth knowing.
Source: research/13-architecture-center-reference-archs.md §1, §4, §6; generated 2026-09-08; verified-on CLI 3.91.0

## 1. URL grammar

| Form | What it is |
|---|---|
| `https://docs.oracle.com/en/solutions/<slug>/` | a reference architecture or solution playbook — a **static book**. `index.html` opens it; the rest are flat siblings (`architecture1.html`, `change-log-*.html`), and each page's last in-book `href` is the next page, so the chain walks with no JS [verified] |
| `https://docs.oracle.com/en/learn/<slug>/` | a step-by-step **tutorial**, a different root. Never cite as a design |
| `https://docs.oracle.com/en/solutions/` | the index — **302 → `/solutions/`** — an Oracle JET SPA: a 4,202-byte shell whose `js/bundle.js` 404s outside the app's routing; no `sitemap.xml`, no `solutions.json` [verified]. **Never scrape it** |
| `https://docs.oracle.com/solutions/?q=<terms>&cType=reference-architectures,solution-playbook&product=<Product+Name>&technologies=<Terraform>&sort=date-desc&lang=en` | the **filter URL**, a real addressable query surface [verified 200]. Not machine-readable; hand it to a human as the "go look here" pointer |

`cType` values: `reference-architectures`, `solution-playbook`.

## 2. Code links: the `pls/topic/lookup` resolver

Solution pages carry no bare `github.com` href, only
`href="/pls/topic/lookup?ctx=en/solutions/<slug>&id=<key>"`. Resolve it before naming a repo:

```bash
curl -sS -o /dev/null -w '%{url_effective}\n' -L \
  'https://docs.oracle.com/pls/topic/lookup?ctx=en/solutions/hub-spoke-network-drg&id=github-oci-arch-hub-spoke-drg'
# -> https://github.com/oracle-devrel/terraform-oci-arch-hub-spoke-drg
```

| `id=` convention | Resolves to |
|---|---|
| `github-*` | a GitHub repo |
| `*-zip` | a Resource Manager one-click URL: `https://cloud.oracle.com/resourcemanager/stacks/create?region=home&zipUrl=…/download/<stack>-latest.zip` [verified on 5 solutions] |

The **RM URL is the safe apply path**: the human clicks it in their own console, so the agent never
holds tenancy-admin credentials.

## 3. Staleness and trap rules

1. **The `terraform-oci-arch-*` family is frozen.** All 85 `oracle-devrel` repos so named were last
   pushed **2025-01-21 or earlier**; `…-web-ha` is **archived**; `…-hub-spoke-drg`'s latest release is
   **v1.3, 2022-09-26** [gh api verified]. `oci-landing-zones/*` is pushed weekly. **Cite `arch-*` as a
   worked example and diagram source; cite `oci-landing-zones/*` as something to run.**
2. **`created` is not `updated`.** Only `dcterms.created` is published; a 2020–2021 date means the
   component list predates DRG v2, ZPR, Security Zones and FSDR. Print the date with the link.
3. **Never construct an AC URL.** `deploy-baseline-lz/` 404s; pillar slugs
   `oci-best-practices-{reliability,performance,operations,distributed-cloud}` 404 while
   `-networking` and `-security` resolve [verified]. Fetch, then cite.
4. **Never scrape `/en/solutions/`.** Use the §1 filter URL as a human pointer.
5. **Code links are `pls/topic/lookup` redirects.** Resolve with §2's one-liner.
6. **The RM URL is the safe apply path**, constructible for any public repo zip.
7. **`/en/solutions/` ≠ `/en/learn/`.** A `learn` page is a tutorial, not a reference architecture.

## 4. The 25 reference architectures

All 25 fetched 2026-09-08: **HTTP 200** [verified]. Slug prefix `https://docs.oracle.com/en/solutions/`.
Stack shorthand: `arch-*` = `oracle-devrel/terraform-oci-arch-*` (frozen, rule 1); `LZ core` =
`oci-landing-zones/terraform-oci-core-landingzone`; **+RM** = page carries a one-click RM URL;
`—` = no code.

| Slug, created | Use when | Stack |
|---|---|---|
| `cis-oci-benchmark`, 2025-02-20 | CIS / greenfield tenancy — **default for governance** | `LZ core` +RM |
| `deploy-partners-to-cis-lz`, 2021-10-29 | a named NGFW vendor is mandated; on the **retired** CIS LZ | `oracle-quickstart/oci-<vendor>` |
| `hub-spoke-network-drg`, 2025-08-29 | connect VCNs, transit, on-prem — **default multi-VCN topology** | `arch-hub-spoke-drg` +RM |
| `hub-spoke-network`, 2025-08-28 | same via LPGs; only if LPGs already exist, else prefer the DRG row | `arch-hub-spoke` (pinned `v1.1.2`) +RM |
| `oci-network-deployment`, 2024-01-17 | design reasoning: CIDR plan, public vs private, gateways | links `oci-cis-landingzone-quickstart` |
| `oci-best-practices-networking`, 2025-10-08 | review a network design; newest networking guidance | — |
| `oci-tenancy-cyber-resilience-architecture`, 2026-08-03 | ransomware, immutable backup — **newest page here** | — |
| `ha-web-app`, 2021-11-22 | canonical LB → multi-FD web tier → ADB private endpoint | `arch-web-ha` **archived** +RM |
| `oci-pilot-light-dr`, 2021-07-12 | cost-constrained DR, RTO in tens of minutes | — |
| `mid-tier-replication-oci-dr-arch`, 2025-10-31 | app-tier DR when the DB already has Data Guard | — |
| `standby-database-in-cloud`, 2021-02-22 | on-prem primary → OCI standby via Data Guard | — |
| `dr-oci-to-oracle-compute-cloud-at-customer`, 2026-02-23 | residency forbids a 2nd public region | — |
| `full-stack-dr-weblogic-platform`, 2024-06-11 | WebLogic / FMW DR; reference for FSDR plan design | — |
| `oracle-analytics-cloud-disaster-recovery`, 2024-10-21 | OAC DR; FSDR user-defined scripts | `oracle-samples/full-stack-disaster-recovery` |
| `epm-dr-arch-oci`, 2024-10-23 | EPM / Hyperion DR; "replicate every storage class" | — |
| `cross-region-dr-essbase-oci`, 2025-10-20 | Essbase cross-region DR; current FSDR idioms | — |
| `oracle-data-integrator-dr`, 2024-05-13 | ODI / ETL DR; which resource types replicate | — |
| `deploy-xreg-dr-rackware`, 2021-05-24 | RackWare block replication when native misses the guest | — |
| `implement-dr-for-ocvs`, 2020-12-08 | OCVS SDDC DR — **oldest here, re-verify first** | — |
| `cloud-native-ecommerce`, 2025-04-28 | MuShop on OKE + ATP — best "real OKE app" | `oracle-quickstart/oci-cloudnative` +RM |
| `deploy-microservices`, 2023-11-29 | smallest runnable OKE reference | `arch-microservice-oke` +RM |
| `oci-service-mesh-oke`, 2024-11-05 | mTLS / traffic shifting on OKE without Istio | `arch-service-mesh-oke` (repo verified; page link unresolved) |
| `oci-apm-for-microservices`, 2025-03-10 | "where is the latency" on OKE | — |
| `deploy-autonomous-database-and-app`, 2022-06-23 | expose an APEX/ADB app safely: **ATP private endpoint + NSG** | `oracle-devrel/terraform-oci-oracle-cloud-foundation` |
| `oci-multicloud-genai-rag`, **2026-04-24** | current GenAI RAG — prefer to `implement-rag-oci` (2024-09-24) | — |

## 5. Hard rules

- Fetch before citing; never build an AC URL; print the `created` date beside the link.
- Resolve `pls/topic/lookup` before naming a repo; propose the RM URL, never run the apply.
- These 25 are "the most relevant found", not a ranked slice — no machine-readable index exists.
