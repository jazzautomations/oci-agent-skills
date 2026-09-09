Purpose: live-checked `docs.oracle.com` URLs skills and evals may cite, plus known-404s as CI link-checker negative fixtures.
Source: research/04c-core-services-pitfalls.md, research/13-architecture-center-reference-archs.md, research/17-eval-task-corpus.md; generated 2026-09-08; verified-on CLI 3.91.0

Checked 2026-09-09: `curl -sI -o /dev/null -w "%{http_code}"` ±`-L`.
Prefixes: `P1` = `https://docs.oracle.com/en-us/iaas/Content/` · `P2` = `.../en/solutions/` · `P3` = `.../en-us/iaas/`

## 1. Verified 200 under `P1`
Cell = `<subdir>: <page>`; C/R/T = Concepts/References/Tasks; append `.htm` unless noted.

| Group | Pages |
|---|---|
| APIGateway | C: apigatewayoverview · home |
| Balance | C: balanceoverview |
| Bastion | C: bastionoverview · T: managingsessions |
| Billing | C: costanalysisoverview |
| Block | C: blockvolumebackups, overview, volumegroups · T: resizingavolume |
| Compute | C: computeoverview · R: bestpracticescompute, computeshapes, serialconsole · T: gettingmetadata, launchinginstance, manage-plugins, reserve-capacity, resizinginstances |
| ContEng | C: contengoverview |
| DNS | T: privatedns |
| Events | C: eventsoverview |
| File | C: filestorageoverview · T: managingmounttargets, managingsnapshots |
| FreeTier | freetier_topic-Always_Free_Resources |
| Functions | C: functionsoverview |
| GSG | C: baremetalintro |
| Identity | Reference: policyreference · dynamicgroups: managingdynamicgroups |
| KeyManagement | C: keyoverview · T: managingsecrets |
| Logging | C: loggingoverview |
| Monitoring | C: monitoringoverview |
| Network | C: networksecuritygroups, overview, securitylists · T: NATgateway, localVCNpeering, managingIPaddresses, managingVCNs, servicegateway |
| NetworkLoadBalancer | introduction |
| Notification | home |
| Object | C: objectstorageoverview · T: usinglifecyclepolicies, usingmultipartuploads, usingpreauthenticatedrequests, usingreplication |
| ResourceManager | C: resourcemanager |
| cloud-adoption-framework | bare dir URL, **no `.htm`** (`index.htm` = 404) · high-availability, disaster-recovery |
| cloud-guard | home |
| container-instances | home |
| devops | using: home |
| generative-ai | overview, pretrained-models, regions |
| generative-ai-agents | overview |
| language | using: overview |

## 2. Verified 200 elsewhere
| URL |
|---|
| `P3`tools/oci-cli/latest/oci_cli_docs/index.html |
| `P3`autonomous-database-serverless/doc/autonomous-provision.html |
| `P3`disaster-recovery/index.html |
| `P2`oci-best-practices/index.html |
| `P2`oci-best-practices-networking/index.html |

## 3. 3xx — cite the resolved target
| Requested | Resolved 200 |
|---|---|
| `P1`Block/Tasks/attachingavolume.htm | `P1`Block/Tasks/attach-compute-volume-attachment.htm |
| `P1`General/Concepts/servicelimits.htm | `P1`General/service-limits/default.htm |
| `P3`data-science/using/data-science.htm | `P1`data-science/using/home.htm |
| `P3`security-zone/using/security-zones.htm | `P1`security-zone/using/security-zones.htm |
| `P2`oci-best-practices-security/index.html | `P2`oci-best-practices/effective-strategies-security-and-compliance1.html |

## 4. Negative fixtures (never 200)
| URL | 2026-09-09 |
|---|---|
| `P2`deploy-baseline-lz/index.html | 404 |
| `P2`oci-best-practices-reliability/index.html | 404 |
| `P2`oci-best-practices-performance/index.html | 404 |
| `P2`oci-best-practices-distributed-cloud/index.html | 404 |
| `P2`oci-best-practices-operations/index.html | 302 → `P2`oci-best-practices/…-efficiency1.html (404); bare and `-L` both fail |

## 5. Rules
1. Never build a URL by pattern — the `oci-best-practices-*` slugs 404 more often than not.
2. Record the bare code *and* the `-L` target — a 302 can land on a 404 (§4); cite a 3xx only via a 200 target.
3. AC pages carry `dcterms.created`, not an updated date — print it. Never scrape the `/en/solutions/` listing (JS shell, no sitemap).
4. A URL absent here is not citable: add it with its status code and date first.
