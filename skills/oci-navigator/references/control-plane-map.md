Purpose: user intent -> Oracle product -> the control plane that actually owns it, including the products where the OCI CLI stops at the instance envelope and the ones with no OCI control plane at all.
Source: research/09c §A1-A7, research/11 §15, research/16 §A; generated 2026-09-08; verified-on CLI 3.91.0

## Contents

1 how to read · 2 databases · 3 OS, Java, runtimes · 4 app platform (envelope-only) ·
5 marketplace and distributed cloud · 6 AI and data · 7 SaaS and health · 8 fleet and long tail

## 1. How to read

"CLI group" = the `oci <group> <noun>` root to hand to the owning skill. **elsewhere** = stop:
name the console/API that owns it and hand off; do not emit an `oci` command. **envelope** = the
CLI creates, sizes and moves the *instance*; every business object inside it lives in that
product's own REST API. All rows `[verified]` from `--help` on 3.91.0 unless marked otherwise.

## 2. Databases — five noun-sets, not one

| Intent | Product | Control plane |
|---|---|---|
| managed MySQL, HeatWave analytics/AutoML | MySQL HeatWave | `oci mysql db-system`, `... db-system heatwave-cluster` |
| Oracle DB on a VM I control | Base Database | `oci db system` -> `db-home` -> `database` |
| Exadata in an OCI region | ExaCS | `oci db cloud-exa-infra` + `oci db cloud-vm-cluster` |
| elastic Exadata, no rack sizing | ExaDB-XS | `oci db exascale-db-storage-vault` + `oci db exadb-vm-cluster` |
| Exadata in my datacenter | ExaDB-C@C | `oci db exadata-infrastructure` + `oci db vm-cluster` (+ `oci datacc`) |
| Oracle DB inside Azure/AWS/GCP | Database@\<cloud\> | `oci multicloud` (anchors/subs); `oci dbmulticloud` (keys, blob mounts) |
| self-driving DB, no DBA | Autonomous | `oci db autonomous-database` |
| sharded / globally distributed | Globally Distributed DB | `oci distributed-database` (and `-v26`, an API-version split `[unverified]`) |

Never assume "Oracle database on OCI" means Autonomous. Pick the noun-set from the *hardware
story* the user described, then hand to `oracle-autonomous-db` or `oracle-db-fleet`.

## 3. OS, Java, runtimes

| Intent | Product | Control plane |
|---|---|---|
| patch my Linux fleet | OS Management Hub | `oci os-management-hub` |
| is the agent up / run a command on the box | Oracle Cloud Agent | `oci instance-agent plugin\|command` |
| which Java runtimes are in my estate | Java Management Service | `oci jms fleet`, `oci jms-utils` |
| download an entitled JDK | JMS Java Downloads | `oci jms-java-downloads` |
| AOT-compile my Java app | Oracle GraalVM | **no OCI control plane** — build tooling / `oci devops` |
| run or patch a WebLogic domain | WLS for OCI + WLMS | Marketplace stack -> `oci wlms wls-domain` |
| deploy my Helidon/Micronaut service | framework only | `oci compute` / `oci ce` / `oci container-instances` / `oci fn` |

## 4. Application platform — envelope only

`oci <group> <noun>-instance` creates/starts/stops/scales the instance. Integrations, reports,
dialog flows, pages and assets are **not** reachable from the CLI.

| Product | CLI group | Business objects live in |
|---|---|---|
| Oracle Integration (OIC) | `oci integration integration-instance` | OIC REST API |
| Analytics Cloud (OAC) | `oci analytics analytics-instance` | OAC REST API |
| Digital Assistant (ODA) | `oci oda` | **exception**: 95 of 119 leaves reach the content plane |
| Visual Builder / VB Studio | `oci visual-builder vb-instance`, `oci vbstudio instance` | VB / VB Studio APIs |
| Process Automation (OPA) | `oci opa opa-instance` | OPA REST (or OIC `enable-process-automation`) |
| Content Management (OCE) | `oci oce oce-instance` | OCM REST API |

## 5. Marketplace and distributed cloud

| Intent | Control plane |
|---|---|
| find/deploy a partner image or stack | `oci marketplace listing\|package\|accepted-agreement` -> `oci resource-manager stack` |
| private internal catalogue | `oci service-catalog private-application` |
| OCI compute in my datacenter | `oci ccc infrastructure` + a rack-local endpoint |
| a whole OCI region on-prem (Dedicated Region) | **no group — it *is* a region**: `--region` / `--endpoint`; ids are not published |
| disconnected / edge node | `oci rover node\|standalone-cluster\|station-cluster` |
| OCI Alloy (partner-operated) | absent from the SDK realm table — unknown realm, no assumption |

## 6. AI and data

| Intent | Control plane |
|---|---|
| read text from an image | `oci ai-vision analyze-image` |
| sentiment / PII / translation | `oci ai language batch-detect-*` (nested group, **not** `oci ai-language`) |
| transcribe audio / TTS | `oci speech transcription-job\|synthesize-speech` |
| extract fields from invoices | `oci ai-document processor-job` |
| detect anomalies in sensor data | service **removed in CLI 3.65** — `oci data-science` or GenAI |
| unexpected spend spike | `oci costad cost-anomaly-monitor` (FinOps, unrelated to the above) |
| train / host a custom model | `oci data-science` + `oci model-deployment` |
| managed Hyperledger Fabric | `oci blockchain blockchain-platform` |
| send mail from an app | `oci email` (config) + `oci email-data-plane email-submitted-response submit-email` |

## 7. SaaS and health — hand off

| Intent | Control plane |
|---|---|
| refresh my Fusion test environment | `oci fusion-apps refresh-activity` (envelope) |
| change a Fusion ERP config, run a BIP report | **elsewhere** — Fusion console + REST/BIP/BICC |
| NetSuite anything | **elsewhere** — SuiteTalk/SuiteScript, often via an OIC adapter |
| EHR / clinical data | **elsewhere** — Oracle Health consoles; `oci ddfs` only for device FHIR ingest |
| SOC 2 / PCI attestation | **elsewhere** — Console only; no `oci compliance` group exists |

## 8. Fleet and long tail

`oci fleet-apps-management` (patch compliance of *your* fleet) · `oci fleet-software-update`
(Exadata Fleet Update) · `oci capacity-management` (OCC enterprise capacity contract, usually
`NotAuthorizedOrNotFound`; not service limits) · `oci bds` (managed Hadoop) · `oci batch` ·
`oci ocvs` (VMware) · `oci media-services` · `oci iot` (domain-group, domain, digital-twin-*)
· `oci desktops` · `oci mngdmac`. Routing entries only — these have no dedicated skill.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| NotFound | Wrong static path / wrong API version / typo'd service endpoint | id 14 [unverified] |
| NotAuthorizedOrNotFound | Deliberate ambiguity: missing resource OR missing policy OR wrong region OR wrong compartment | id 13 [unverified] |
