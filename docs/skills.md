# Skills catalog

[Documentation](README.md) · [MCP tools](mcp-tools.md)

Generated from `skills/*/SKILL.md`; regenerate with `uv run --frozen --project runtime python scripts/doc-gen/catalogs.py`.

**37 skills** · 12 read-only · 25 guarded-write. Verification labels: 0 live, 19 partial, 18 shape-only.

`partial` means selected reads have recorded live evidence; `shape-only` means command syntax was checked. Neither label certifies a complete workflow. Guarded-write describes recipes requiring a change plan and authorization; all bundled helper scripts and MCP tools remain read-only.

Script counts include both shell entrypoints and Python helpers. Reference counts cover skill-local Markdown; shared resources are linked separately.

## Navigation, identity & governance

| Skill | Purpose | Mode | Evidence | Scripts | Local refs | Shared resources |
|---|---|---|---|---:|---:|---|
| [oci-navigator](../skills/oci-navigator/SKILL.md) | Locates services and CLI groups on the current OCI platform. | read-only | partial | 0 | 4 | [architecture-center.md](../references/architecture-center.md), [console-links.md](../references/console-links.md), [realms-endpoints.md](../references/realms-endpoints.md), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oci-cli-auth](../skills/oci-cli-auth/SKILL.md) | Fixes OCI CLI authentication, identity and query problems. | read-only | partial | 2 | 2 | [auth-modes.md](../references/auth-modes.md), [error-triage.md](../references/error-triage.md), [jmespath.md](../references/jmespath.md), [realms-endpoints.md](../references/realms-endpoints.md), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md), [windows-powershell.md](../references/windows-powershell.md) |
| [oci-tenancy-governance](../skills/oci-tenancy-governance/SKILL.md) | Designs and audits OCI tenancy guardrails: compartment topology, tag namespaces, cost-tracking tags, quotas, budgets, landing zones, organizations and child tenancies. | guarded-write | partial | 2 | 5 | [architecture-center.md](../references/architecture-center.md), [cross-service-pitfalls.md](../references/cross-service-pitfalls.md), [error-corpus.json](../references/error-corpus.json), [iam-variables.md](../references/iam-variables.md), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oci-iam-policy](../skills/oci-iam-policy/SKILL.md) | Writes and reviews OCI IAM policy and identity-domain configuration: verbs, resource-type families, conditions, dynamic groups, federation (SAML/OIDC), SCIM, MFA and sign-on policies, cross-tenancy Endorse/Admit/Define. | guarded-write | partial | 2 | 3 | [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [iam-variables.md](../references/iam-variables.md), [redaction.md](../references/redaction.md), [resource-type-families.json](../references/resource-type-families.json), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oci-support-limits](../skills/oci-support-limits/SKILL.md) | Answers "can I actually create this" and files the request when the answer is no: service limits vs compartment quotas vs physical capacity, resource-availability per AD, limit-increase requests, and OCI support incidents. | guarded-write | partial | 1 | 4 | [console-links.md](../references/console-links.md), [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md) |

## Compute, network & storage

| Skill | Purpose | Mode | Evidence | Scripts | Local refs | Shared resources |
|---|---|---|---|---:|---:|---|
| [oci-compute](../skills/oci-compute/SKILL.md) | Launches, resizes and triages OCI Compute. | guarded-write | partial | 2 | 4 | [cross-service-pitfalls.md](../references/cross-service-pitfalls.md), [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [jmespath.md](../references/jmespath.md), [operator-contract.md](../references/operator-contract.md), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oci-networking](../skills/oci-networking/SKILL.md) | Builds and debugs OCI VCN networking. | guarded-write | partial | 1 | 7 | [architecture-center.md](../references/architecture-center.md), [cross-service-pitfalls.md](../references/cross-service-pitfalls.md), [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [jmespath.md](../references/jmespath.md), [operator-contract.md](../references/operator-contract.md), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oci-object-storage](../skills/oci-object-storage/SKILL.md) | Operates OCI Object Storage. | guarded-write | partial | 1 | 4 | [cross-service-pitfalls.md](../references/cross-service-pitfalls.md), [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [operator-contract.md](../references/operator-contract.md), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oci-block-file-storage](../skills/oci-block-file-storage/SKILL.md) | Operates OCI Block, boot and File Storage. | guarded-write | shape-only | 1 | 3 | [cross-service-pitfalls.md](../references/cross-service-pitfalls.md), [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [operator-contract.md](../references/operator-contract.md), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oci-bastion-access](../skills/oci-bastion-access/SKILL.md) | Reaches a private OCI host or database through OCI Bastion. | guarded-write | shape-only | 1 | 2 | [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [operator-contract.md](../references/operator-contract.md), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md) |

## Delivery & infrastructure as code

| Skill | Purpose | Mode | Evidence | Scripts | Local refs | Shared resources |
|---|---|---|---|---:|---:|---|
| [oci-oke](../skills/oci-oke/SKILL.md) | Creates and operates OKE Kubernetes clusters. | guarded-write | shape-only | 1 | 7 | [architecture-center.md](../references/architecture-center.md), [auth-modes.md](../references/auth-modes.md), [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [operator-contract.md](../references/operator-contract.md), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oci-devops-pipelines](../skills/oci-devops-pipelines/SKILL.md) | Builds OCI DevOps CI/CD. | guarded-write | shape-only | 1 | 5 | [auth-modes.md](../references/auth-modes.md), [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [operator-contract.md](../references/operator-contract.md), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oci-serverless](../skills/oci-serverless/SKILL.md) | Deploys OCI Functions, Container Instances and API Gateway. | guarded-write | shape-only | 1 | 3 | [auth-modes.md](../references/auth-modes.md), [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [operator-contract.md](../references/operator-contract.md), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oci-terraform](../skills/oci-terraform/SKILL.md) | Authors and reviews OCI Terraform/OpenTofu and drives Resource Manager stacks. | guarded-write | shape-only | 1 | 8 | [architecture-center.md](../references/architecture-center.md), [auth-modes.md](../references/auth-modes.md), [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [operator-contract.md](../references/operator-contract.md), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md) |

## Operations & security

| Skill | Purpose | Mode | Evidence | Scripts | Local refs | Shared resources |
|---|---|---|---|---:|---:|---|
| [oci-monitoring-alarms](../skills/oci-monitoring-alarms/SKILL.md) | Queries OCI metrics and sets alarms, including Stack Monitoring. | guarded-write | partial | 2 | 6 | [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [jmespath.md](../references/jmespath.md), [operator-contract.md](../references/operator-contract.md), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oci-logging-audit](../skills/oci-logging-audit/SKILL.md) | Searches OCI logs and Audit events. | read-only | partial | 2 | 5 | [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [jmespath.md](../references/jmespath.md), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oci-incident-triage](../skills/oci-incident-triage/SKILL.md) | Read-only runbook for an OCI resource that is down or degraded: alarm state, recent Audit mutations, Cloud Guard, metrics, logs, work requests, maintenance events and limits, then ranked hypotheses. | read-only | partial | 2 | 2 | [console-links.md](../references/console-links.md), [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oci-security-posture](../skills/oci-security-posture/SKILL.md) | Audits OCI security posture against CIS. | read-only | partial | 2 | 5 | [error-corpus.json](../references/error-corpus.json), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oci-vault-certificates](../skills/oci-vault-certificates/SKILL.md) | Handles OCI Vault, KMS keys, Secrets and Certificates. | guarded-write | partial | 2 | 3 | [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [operator-contract.md](../references/operator-contract.md), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md) |

## Cost & Free Tier

| Skill | Purpose | Mode | Evidence | Scripts | Local refs | Shared resources |
|---|---|---|---|---:|---:|---|
| [oci-cost-analysis](../skills/oci-cost-analysis/SKILL.md) | Explains an OCI bill and estimates cost before provisioning: `usage-api` summarized usage, cost and FOCUS exports, budgets and alert rules, cost-tracking tags, and the credential-free Price List API. | read-only | partial | 4 | 7 | [error-corpus.json](../references/error-corpus.json), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oci-free-tier](../skills/oci-free-tier/SKILL.md) | Survives OCI Free Tier and trials. | read-only | partial | 1 | 3 | [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oci-finops-waste](../skills/oci-finops-waste/SKILL.md) | Finds unused OCI resources and prices potential waste. | read-only | partial | 2 | 2 | [redaction.md](../references/redaction.md), [untrusted-output.md](../references/untrusted-output.md) |

## Oracle Database & APEX

| Skill | Purpose | Mode | Evidence | Scripts | Local refs | Shared resources |
|---|---|---|---|---:|---:|---|
| [oracle-autonomous-db](../skills/oracle-autonomous-db/SKILL.md) | Provisions and connects Oracle Autonomous Database. | guarded-write | shape-only | 1 | 4 | [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [redaction.md](../references/redaction.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oracle-db-fleet](../skills/oracle-db-fleet/SKILL.md) | Operates OCI non-Autonomous database services and enrolled Database Management fleets. | guarded-write | shape-only | 0 | 6 | [cross-service-pitfalls.md](../references/cross-service-pitfalls.md), [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [redaction.md](../references/redaction.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oracle-db-vector-ai](../skills/oracle-db-vector-ai/SKILL.md) | Builds vector search and Select AI inside Oracle Database 26ai/23ai. | guarded-write | shape-only | 0 | 6 | [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [redaction.md](../references/redaction.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oracle-db-sql-access](../skills/oracle-db-sql-access/SKILL.md) | Configures agent SQL access with database-enforced read privileges, SQLcl MCP, ORDS and Database Tools. | guarded-write | shape-only | 0 | 3 | [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [redaction.md](../references/redaction.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oracle-apex](../skills/oracle-apex/SKILL.md) | Delivers Oracle APEX. | guarded-write | shape-only | 0 | 5 | [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [redaction.md](../references/redaction.md), [untrusted-output.md](../references/untrusted-output.md) |

## AI & data

| Skill | Purpose | Mode | Evidence | Scripts | Local refs | Shared resources |
|---|---|---|---|---:|---:|---|
| [oci-generative-ai](../skills/oci-generative-ai/SKILL.md) | Discovers OCI GenAI models and plans chat, embeddings, clusters and agents. | guarded-write | partial | 2 | 8 | [architecture-center.md](../references/architecture-center.md), [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oci-ai-services](../skills/oci-ai-services/SKILL.md) | Uses OCI pretrained AI services: Vision, Language (nested `oci ai language`) sentiment/PII/translation, Speech transcription and TTS, Document Understanding. | read-only | shape-only | 0 | 4 | [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oci-data-platform](../skills/oci-data-platform/SKILL.md) | Moves and processes data on OCI: Streaming (Kafka-compatible) and Queue, Data Flow Spark, Data Integration, Data Catalog, GoldenGate CDC, Big Data Service, Batch, OpenSearch, Redis, and Data Science jobs and model deployments. | guarded-write | shape-only | 0 | 5 | [cross-service-pitfalls.md](../references/cross-service-pitfalls.md), [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md) |

## Reliability & migration

| Skill | Purpose | Mode | Evidence | Scripts | Local refs | Shared resources |
|---|---|---|---|---:|---:|---|
| [oci-dr-backup](../skills/oci-dr-backup/SKILL.md) | Plans OCI resilience and proves it: Full Stack DR protection groups and drills, cross-region backup and replication, AD and fault-domain spread, and RPO/RTO evidence. | guarded-write | partial | 0 | 4 | [architecture-center.md](../references/architecture-center.md), [cross-service-pitfalls.md](../references/cross-service-pitfalls.md), [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oci-migration-patching](../skills/oci-migration-patching/SKILL.md) | Migrates and patches OCI fleets: Cloud Migrations, Cloud Bridge, Database Migration and ZDM, Rover, OS Management Hub, Ksplice, Java Management Service, Fleet Application Management, Exadata Fleet Update, OCVS. | guarded-write | shape-only | 0 | 6 | [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oci-migration-assess](../skills/oci-migration-assess/SKILL.md) | Normalizes AWS, Azure and GCP inventory for OCI assessment. | read-only | shape-only | 1 | 3 | [redaction.md](../references/redaction.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oci-migration-map](../skills/oci-migration-map/SKILL.md) | Maps cloud inventory to OCI targets and scoped price comparisons. | read-only | shape-only | 1 | 3 | [redaction.md](../references/redaction.md), [untrusted-output.md](../references/untrusted-output.md) |
| [oci-migration-landing-zone](../skills/oci-migration-landing-zone/SKILL.md) | Drafts OCI Core Landing Zone variables from assessed inventory. | guarded-write | shape-only | 1 | 1 | [redaction.md](../references/redaction.md), [untrusted-output.md](../references/untrusted-output.md) |

## SDKs & enterprise applications

| Skill | Purpose | Mode | Evidence | Scripts | Local refs | Shared resources |
|---|---|---|---|---:|---:|---|
| [oci-sdk-patterns](../skills/oci-sdk-patterns/SKILL.md) | Writes OCI SDK code that works. | guarded-write | partial | 2 | 5 | [auth-modes.md](../references/auth-modes.md), [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [realms-endpoints.md](../references/realms-endpoints.md), [redaction.md](../references/redaction.md), [service-command-cards.md](../references/service-command-cards.md), [untrusted-output.md](../references/untrusted-output.md), [windows-powershell.md](../references/windows-powershell.md) |
| [oracle-enterprise-apps](../skills/oracle-enterprise-apps/SKILL.md) | Distinguishes OCI service-instance operations from Oracle application APIs. | read-only | shape-only | 0 | 5 | [error-corpus.json](../references/error-corpus.json), [error-triage.md](../references/error-triage.md), [realms-endpoints.md](../references/realms-endpoints.md), [redaction.md](../references/redaction.md), [untrusted-output.md](../references/untrusted-output.md) |

## Choosing a skill

The triggers below are copied from the shipped descriptions. Command samples are the first three read fences; define their variables using the skill's **Scope check** before running them. Outputs are bounded samples.

<details><summary><strong>oci-ai-services</strong></summary>

[Open skill](../skills/oci-ai-services/SKILL.md)

**Use when:** OCR, read text from an image, sentiment, PII detection, translate, transcribe audio, text to speech, invoice or receipt extraction, document AI, extrair texto de PDF.

**Not for:** LLM chat or embeddings (`oci-generative-ai`).

```bash
oci ai-vision project-collection list-projects --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data.items[].{id:id,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci ai-vision model-collection list-models --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data.items[].{id:id,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci ai language project list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data.items[].{id:id,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

</details>

<details><summary><strong>oci-bastion-access</strong></summary>

[Open skill](../skills/oci-bastion-access/SKILL.md)

**Use when:** bastion, jump host, tunnel, "ssh into a private instance", port forward, reach the DB on 1521, managed SSH session, session expired, CIDR allow-list, acessar host privado.

**Not for:** designing the VCN (`oci-networking`) or SSH keys and cloud-init (`oci-compute`).

```bash
oci bastion bastion list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data[].{id:id,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci bastion bastion get --bastion-id "$BASTION_ID" --query 'data.{subnet:"target-subnet-id",allowed:"client-cidr-block-allow-list",state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci bastion session list --bastion-id "$BASTION_ID" --limit 20 --query 'data[].{id:id,state:"lifecycle-state",ttl:"session-ttl-in-seconds"}' --profile "$PROFILE" --region "$REGION"
```

</details>

<details><summary><strong>oci-block-file-storage</strong></summary>

[Open skill](../skills/oci-block-file-storage/SKILL.md)

**Use when:** block volume, boot volume, resize a disk, iSCSI vs paravirtualized attach, multi-attach, volume group, backup policy, clone vs backup, VPU performance tier, growfs, FSS, mount target, NFS export, disco cheio.

**Not for:** object buckets and PARs (`oci-object-storage`).

```bash
oci bv volume list --compartment-id "$COMPARTMENT_ID" --availability-domain "$AD" --limit 20 --query 'data[].{id:id,size:"size-in-gbs",vpu:"vpus-per-gb"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci bv boot-volume list --compartment-id "$COMPARTMENT_ID" --availability-domain "$AD" --limit 20 --query 'data[].{id:id,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci compute volume-attachment list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data[].{volume:"volume-id",state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

</details>

<details><summary><strong>oci-cli-auth</strong></summary>

[Open skill](../skills/oci-cli-auth/SKILL.md)

**Use when:** 401, 403, NotAuthenticated, NotAuthorizedOrNotFound, expired session token, "wrong tenancy", "which profile am I", `--query` returns null, list silently truncated, `--wait-for-state` hangs, work request stuck, não autorizado.

**Not for:** writing IAM policy (`oci-iam-policy`) or SDK code (`oci-sdk-patterns`).

```bash
oci iam region-subscription list --tenancy-id "$T" --all \
  --query 'data[].{region:"region-name",key:"region-key",home:"is-home-region"}'
```

```bash
oci iam user get --user-id "$U" --query 'data.{name:name,mfa:"is-mfa-activated"}'
```

```bash
oci iam compartment list --compartment-id "$T" --compartment-id-in-subtree true \
  --access-level ANY --query 'data[].{name:name,state:"lifecycle-state",id:id}' --limit 20
```

</details>

<details><summary><strong>oci-compute</strong></summary>

[Open skill](../skills/oci-compute/SKILL.md)

**Use when:** launch instance, VM won't start, flexible shape, `.Flex`, image OCID, availability domain, cloud-init, boot volume, serial console, instance pool, autoscaling, A1 ARM, instância não sobe.

**Not for:** out-of-capacity and limits (`oci-support-limits`), reachability (`oci-networking`), private-host access (`oci-bastion-access`).

```bash
oci iam availability-domain list --compartment-id "$TENANCY_ID" --query 'data[].name' --profile "$PROFILE" --region "$REGION"
```

```bash
oci compute shape list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data[].{shape:shape,ocpu:"ocpu-options",memory:"memory-options"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci compute image list --compartment-id "$COMPARTMENT_ID" --operating-system "Oracle Linux" --operating-system-version "9" --shape "$SHAPE" --sort-by TIMECREATED --sort-order DESC --limit 1 --query 'data[].{id:id,name:"display-name"}' --profile "$PROFILE" --region "$REGION"
```

</details>

<details><summary><strong>oci-cost-analysis</strong></summary>

[Open skill](../skills/oci-cost-analysis/SKILL.md)

**Use when:** "why did the bill go up", cost analysis, showback, chargeback, FOCUS, budget, "how much would X cost", egress price, a conta subiu.

**Not for:** Always Free allotments (`oci-free-tier`).

```bash
oci usage-api usage-summary request-summarized-usages --tenant-id "$TENANCY_ID" --time-usage-started "$FROM" --time-usage-ended "$TO" --granularity MONTHLY --group-by '["service"]' --limit 50 --query 'data.items[].[service,"computed-amount"]'
```

```bash
oci usage-api usage-summary request-summarized-usages --tenant-id "$TENANCY_ID" --time-usage-started "$FROM" --time-usage-ended "$TO" --granularity DAILY --group-by '["service","skuName"]' --limit 200 --query 'data.items[].["time-usage-started","sku-name","computed-amount"]'
```

```bash
oci usage-api usage-summary request-summarized-usages --tenant-id "$TENANCY_ID" --time-usage-started "$FROM" --time-usage-ended "$TO" --granularity MONTHLY --group-by-tag '[{"namespace":"Oracle-Tags","key":"CreatedBy"}]' --limit 50 --query 'data.items[].[tags[0].value,"computed-amount"]'
```

</details>

<details><summary><strong>oci-data-platform</strong></summary>

[Open skill](../skills/oci-data-platform/SKILL.md)

**Use when:** Kafka on OCI, stream, queue, Spark job, ETL pipeline, CDC, notebook session, model deployment, BDS, cluster Hadoop.

**Not for:** database-side SQL (`oracle-db-*`).

```bash
oci streaming admin stream list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data[].{id:id,endpoint:"messages-endpoint"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci queue queue-admin queue list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data.items[].{id:id,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci data-flow application list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data[].{id:id,spark:"spark-version"}' --profile "$PROFILE" --region "$REGION"
```

</details>

<details><summary><strong>oci-devops-pipelines</strong></summary>

[Open skill](../skills/oci-devops-pipelines/SKILL.md)

**Use when:** OCI DevOps project, build pipeline, deployment pipeline, `build_spec.yaml`, OCIR, push an image, Artifact Registry, image signing, vulnerability audit stage, trigger, approval stage, GitHub Actions to OCI, pipeline quebrou.

**Not for:** what the pipeline deploys into (`oci-oke`, `oci-serverless`).

```bash
oci devops project list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data.items[].{id:id,name:name,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci devops build-pipeline list --project-id "$PROJECT_ID" --limit 20 --query 'data.items[].{id:id,name:"display-name"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci devops build-run get --build-run-id "$BUILD_RUN_ID" --query 'data.{id:id,state:"lifecycle-state",progress:"build-run-progress"}' --profile "$PROFILE" --region "$REGION"
```

</details>

<details><summary><strong>oci-dr-backup</strong></summary>

[Open skill](../skills/oci-dr-backup/SKILL.md)

**Use when:** disaster recovery, DR drill, failover, switchover, RPO, RTO, cross-region backup, fault domain, "are we highly available", plano de DR.

**Not for:** one service's backup command — ask that service's skill.

```bash
oci disaster-recovery dr-protection-group list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data.items[].{id:id,role:role}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci disaster-recovery dr-plan list --dr-protection-group-id "$DR_GROUP_ID" --limit 20 --query 'data.items[].{id:id,type:"type"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci disaster-recovery dr-plan-execution list --dr-protection-group-id "$DR_GROUP_ID" --limit 20 --query 'data.items[].{id:id,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

</details>

<details><summary><strong>oci-finops-waste</strong></summary>

[Open skill](../skills/oci-finops-waste/SKILL.md)

**Use when:** idle resources, orphan volumes, desperdício OCI.

**Not for:** bill explanation (oci-cost-analysis) or migration assessment.

```bash
oci compute instance list --compartment-id "$COMPARTMENT_ID" --limit 100 --query 'data[].{id:id,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci compute boot-volume-attachment list --compartment-id "$COMPARTMENT_ID" --availability-domain "$AD" --limit 100 --query 'data[].{volume:"boot-volume-id",instance:"instance-id",state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci bv volume list --compartment-id "$COMPARTMENT_ID" --limit 100 --query 'data[].{id:id,gb:"size-in-gbs",vpu:"vpus-per-gb"}' --profile "$PROFILE" --region "$REGION"
```

</details>

<details><summary><strong>oci-free-tier</strong></summary>

[Open skill](../skills/oci-free-tier/SKILL.md)

**Use when:** always free, free tier, trial expired, upgrade to PAYG, out of host capacity on A1/ARM, "did Oracle delete my instance", reclaimed after 7 idle days, the 2-VCN limit, port 25 blocked, $300 credits, conta gratuita.

**Not for:** paid-tenancy bill analysis (`oci-cost-analysis`) or limit increases (`oci-support-limits`).

```bash
oci limits value list --compartment-id "$TENANCY_ID" --service-name compute --name "$LIMIT_NAME" --limit 100 --query 'data[].{n:name,v:value,ad:"availability-domain"}'
```

```bash
oci limits definition list --compartment-id "$TENANCY_ID" --service-name compute --name "$LIMIT_NAME" --limit 10 --query 'data[].{n:name,scope:"scope-type",dyn:"is-dynamic"}'
```

```bash
oci limits resource-availability get --compartment-id "$TENANCY_ID" --service-name vcn --limit-name vcn-count --query 'data.{used:used,available:available,quota:"effective-quota-value"}'
```

</details>

<details><summary><strong>oci-generative-ai</strong></summary>

[Open skill](../skills/oci-generative-ai/SKILL.md)

**Use when:** OCI GenAI, Cohere command, Grok or llama on Oracle, model deprecated, 429 on chat, agent endpoint, knowledge base, RAG on OCI.

**Not for:** in-database vectors (`oracle-db-vector-ai`).

```bash
oci generative-ai model-collection list-models --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data.items[].{id:id,cap:capabilities,retired:"time-deprecated"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci generative-ai endpoint-collection list-endpoints --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data.items[].{id:id,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci generative-ai dedicated-ai-cluster-collection list-dedicated-ai-clusters --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data.items[].{id:id,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

</details>

<details><summary><strong>oci-iam-policy</strong></summary>

[Open skill](../skills/oci-iam-policy/SKILL.md)

**Use when:** "Allow group …", least privilege, dynamic group, "why can't the agent read", federação, política IAM.

**Not for:** auditing existing policy (`oci-security-posture`).

```bash
oci iam domain list --compartment-id "$TENANCY_ID" --limit 20 --query 'data[].{name:"display-name",url:url}'
oci iam region-subscription list --tenancy-id "$TENANCY_ID" --query 'data[?"is-home-region"].{r:"region-name",k:"region-key"}'
```

```bash
oci iam policy list --compartment-id "$COMPARTMENT_ID" --limit 50 --query 'data[].{n:name,at:"compartment-id",st:statements}'
oci iam policy get --policy-id "$POLICY_ID" --query 'data.statements'
```

```bash
oci iam dynamic-group list --compartment-id "$TENANCY_ID" --limit 50 --query 'data[].{n:name,rule:"matching-rule"}'
```

</details>

<details><summary><strong>oci-incident-triage</strong></summary>

[Open skill](../skills/oci-incident-triage/SKILL.md)

**Use when:** "it's down", outage, page fired, "worked yesterday", after the deploy, caiu, ficou lento.

**Not for:** non-OCI incidents, and never the fix — it does not mutate.

</details>

<details><summary><strong>oci-logging-audit</strong></summary>

[Open skill](../skills/oci-logging-audit/SKILL.md)

**Use when:** search the logs, "who deleted", 5xx in the LB log, flow logs, audit event, log group, `logging-search` syntax, LQL, Logging Analytics, Service Connector Hub, the 14-day window, quem apagou.

**Not for:** alarms and metrics (`oci-monitoring-alarms`) or the outage runbook (`oci-incident-triage`).

```bash
oci logging log-group list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data[].{n:"display-name",id:id}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci logging log list --log-group-id "$LOG_GROUP_ID" --limit 20 --query 'data[].{n:"display-name",t:"log-type",s:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci logging-search search-logs --search-query "search \"$COMPARTMENT_ID\" | sort by datetime desc" --time-start "$START_TIME" --time-end "$END_TIME" --limit 50 --query 'data.results[].data.{t:datetime,type:"logContent".type}' --profile "$PROFILE" --region "$REGION"
```

</details>

<details><summary><strong>oci-migration-assess</strong></summary>

[Open skill](../skills/oci-migration-assess/SKILL.md)

**Use when:** inventário para migrar nuvens.

**Not for:** target pricing (oci-migration-map) or patching.

</details>

<details><summary><strong>oci-migration-landing-zone</strong></summary>

[Open skill](../skills/oci-migration-landing-zone/SKILL.md)

**Use when:** landing zone para migração OCI.

**Not for:** applying Terraform (oci-terraform) or source inventory.

```bash
oci resource-manager stack list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data[].{name:"display-name",state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

</details>

<details><summary><strong>oci-migration-map</strong></summary>

[Open skill](../skills/oci-migration-map/SKILL.md)

**Use when:** comparar migração AWS/GCP/Azure para OCI.

**Not for:** inventory collection or current OCI bills.

</details>

<details><summary><strong>oci-migration-patching</strong></summary>

[Open skill](../skills/oci-migration-patching/SKILL.md)

**Use when:** migrate to OCI, lift and shift, ZDM, patch my fleet, yum on OCI, Java estate, VMware on OCI, atualizar frota.

**Not for:** Terraform adoption of existing infra (`oci-terraform`).

```bash
oci cloud-migrations migration list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data.items[].id' --profile "$PROFILE" --region "$REGION"
```

```bash
oci cloud-bridge inventory inventory list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data.items[].id' --profile "$PROFILE" --region "$REGION"
```

```bash
oci database-migration migration list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data.items[].{id:id,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

</details>

<details><summary><strong>oci-monitoring-alarms</strong></summary>

[Open skill](../skills/oci-monitoring-alarms/SKILL.md)

**Use when:** alarm, "alert me when", MQL, metric namespace, no datapoints, CPU utilization, ONS topic, PagerDuty, synthetic monitor, health check, APM, stack monitoring, alarme não dispara.

**Not for:** reading logs or Audit (`oci-logging-audit`) or an active outage (`oci-incident-triage`).

```bash
oci monitoring metric list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data[].{namespace:namespace,name:name}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci monitoring metric-data summarize-metrics-data --compartment-id "$COMPARTMENT_ID" --namespace "$METRIC_NAMESPACE" --query-text "$MQL" --start-time "$START_TIME" --end-time "$END_TIME" --query 'data[].{points:"aggregated-datapoints"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci monitoring alarm list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data[].{id:id,enabled:"is-enabled",severity:severity}' --profile "$PROFILE" --region "$REGION"
```

</details>

<details><summary><strong>oci-navigator</strong></summary>

[Open skill](../skills/oci-navigator/SKILL.md)

**Use when:** unknown OCI product/group, command-name errors, cross-cloud concept mapping to OCI.

**Not for:** Compute Classic/OCI-C terminology or comparisons (even with current OCI), established service operations, database families (`oracle-db-fleet`), application API reach (`oracle-enterprise-apps`).

```bash
# realm, home region, subscriptions
oci iam region-subscription list --tenancy-id ${TENANCY_ID} --query "data[].\"region-name\"" --output json
```

```bash
# cheapest "is the product known here"
oci limits service list --compartment-id ${TENANCY_ID} --limit 100 --query "data[].name" --output json
```

```bash
# does it already hold any
oci search resource structured-search --query-text "query all resources where compartmentId = '${COMPARTMENT_ID}'" --limit 50 --query "data.\"items\"[].\"resource-type\"" --output json
```

</details>

<details><summary><strong>oci-networking</strong></summary>

[Open skill](../skills/oci-networking/SKILL.md)

**Use when:** VCN, subnet, NSG, security list, route table, IGW/NAT/service gateway, DRG, peering, VPN, FastConnect, DNS, load balancer 502, backend unhealthy, "can't reach", timeout, porta 80 não abre.

**Not for:** OKE service annotations (`oci-oke`) or firewall/WAF findings (`oci-security-posture`).

```bash
oci network vcn list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data[].{id:id,cidrs:"cidr-blocks"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci network subnet list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data[].{id:id,vcn:"vcn-id",route:"route-table-id"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci network nsg list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data[].{id:id,vcn:"vcn-id"}' --profile "$PROFILE" --region "$REGION"
```

</details>

<details><summary><strong>oci-object-storage</strong></summary>

[Open skill](../skills/oci-object-storage/SKILL.md)

**Use when:** bucket, namespace, object prefix and paging, pre-authenticated request, PAR, presigned URL, lifecycle rule, versioning, retention lock, replication, `os sync`, multipart cleanup, archive tier, bucket público.

**Not for:** block/boot volumes or NFS (`oci-block-file-storage`).

```bash
oci os ns get --compartment-id "$TENANCY_ID" --query data --profile "$PROFILE" --region "$REGION"
```

```bash
oci os bucket list --compartment-id "$COMPARTMENT_ID" --namespace-name "$NAMESPACE" --limit 20 --query 'data[].{name:name,created:"time-created"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci os object list --namespace-name "$NAMESPACE" --bucket-name "$BUCKET" --prefix "$PREFIX" --limit 20 --query '{items:data[].{name:name,size:size},next:"next-start-with"}' --profile "$PROFILE" --region "$REGION"
```

</details>

<details><summary><strong>oci-oke</strong></summary>

[Open skill](../skills/oci-oke/SKILL.md)

**Use when:** OKE, node pool, virtual nodes, kubeconfig, pod Pending, ErrImagePull, PVC stuck, LoadBalancer not provisioning, cluster upgrade, workload identity, CSI/LB annotations, cluster não sobe.

**Not for:** the CI pipeline that deploys into it (`oci-devops-pipelines`) or the Terraform that creates it (`oci-terraform`).

```bash
oci ce cluster-options get --cluster-option-id all --query 'data."kubernetes-versions"' --profile "$PROFILE" --region "$REGION"
```

```bash
oci ce node-pool-options get --node-pool-option-id all --query 'data.{shapes:shapes,sources:sources}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci ce cluster list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data[].{id:id,type:type,version:"kubernetes-version"}' --profile "$PROFILE" --region "$REGION"
```

</details>

<details><summary><strong>oci-sdk-patterns</strong></summary>

[Open skill](../skills/oci-sdk-patterns/SKILL.md)

**Use when:** oci python sdk, write a script, boto3 equivalent, signer, instance principal in code, resource principal, pagination helper, waiter, retry strategy, circuit breaker, `ServiceError` fields, `opc-request-id`, Java/Go/TypeScript SDK, escrever script OCI.

**Not for:** one-off CLI invocations (`oci-cli-auth`).

```bash
oci iam region list --query 'data[].{key:key,name:name}'
```

```bash
oci iam region-subscription list --tenancy-id "$T" --all \
  --query 'data[].{region:"region-name",home:"is-home-region",status:status}'
```

```bash
oci iam compartment list --compartment-id "$T" --compartment-id-in-subtree true \
  --access-level ACCESSIBLE --lifecycle-state ACTIVE --limit 50 \
  --query 'data[].{name:name,id:id}'
```

</details>

<details><summary><strong>oci-security-posture</strong></summary>

[Open skill](../skills/oci-security-posture/SKILL.md)

**Use when:** "are we secure", tenancy audit, CIS benchmark, compliance check, public bucket, 0.0.0.0/0 ingress, MFA, stale API key, any-user policy, Cloud Guard problem, Data Safe, vulnerability scan, WAF, auditoria de segurança.

**Not for:** writing the fix policy (`oci-iam-policy`) or Oracle's own attestations, which are Console-only.

```bash
oci search resource structured-search --query-text "query bucket, securitylist, networksecuritygroup resources where compartmentId = '$COMPARTMENT_ID'" --limit 100 --query 'data.items[].{t:"resource-type",n:"display-name"}'
```

```bash
oci iam user list --compartment-id "$TENANCY_ID" --query 'data[?"is-mfa-activated"==`false`].{n:name,st:"lifecycle-state"}' --limit 20
```

```bash
oci iam policy list --compartment-id "$COMPARTMENT_ID" --query 'data[].{n:name,broad:statements[?contains(@,`any-user`)||contains(@,`manage all-resources`)]}' --limit 20
```

</details>

<details><summary><strong>oci-serverless</strong></summary>

[Open skill](../skills/oci-serverless/SKILL.md)

**Use when:** OCI Functions, `fn deploy`, serverless, container instance, API Gateway 504, route not matching, resource principal, cold start, image digest, memory or timeout limit, função não responde.

**Not for:** OKE workloads (`oci-oke`) or the build pipeline (`oci-devops-pipelines`).

```bash
oci fn application list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data[].{id:id,architecture:shape,subnets:"subnet-ids"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci fn function list --application-id "$APPLICATION_ID" --limit 20 --query 'data[].{id:id,memory:"memory-in-mbs",timeout:"timeout-in-seconds",digest:"image-digest"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci container-instances container-instance list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data.items[].{id:id,shape:shape,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

</details>

<details><summary><strong>oci-support-limits</strong></summary>

[Open skill](../skills/oci-support-limits/SKILL.md)

**Use when:** out of host capacity, limit reached, quota, "increase my limit", GPU limit is zero, open a ticket/SR, aumentar limite.

**Not for:** pricing (`oci-cost-analysis`).

```bash
oci limits definition list --compartment-id "$TENANCY_ID" --service-name "$SERVICE" --limit 50 --query 'data[].{n:name,scope:"scope-type",dyn:"is-dynamic"}'
```

```bash
oci limits value list --compartment-id "$TENANCY_ID" --service-name "$SERVICE" --limit 50 --query 'data[].{n:name,v:value,ad:"availability-domain"}'
```

```bash
oci limits resource-availability get --compartment-id "$TENANCY_ID" --service-name "$SERVICE" --limit-name "$LIMIT_NAME" --availability-domain "$AD" --query 'data'
```

</details>

<details><summary><strong>oci-tenancy-governance</strong></summary>

[Open skill](../skills/oci-tenancy-governance/SKILL.md)

**Use when:** "make this tenancy safe", landing zone, CIS, compartment structure, tagging strategy, quota, budget alert, estrutura de compartimentos.

**Not for:** policy statements (`oci-iam-policy`) or findings (`oci-security-posture`).

```bash
oci iam compartment list --compartment-id "$TENANCY_ID" --compartment-id-in-subtree true --access-level ANY --limit 100 --query 'data[].name'
```

```bash
oci iam tag-namespace list --compartment-id "$TENANCY_ID" --limit 50 --query 'data[].name'
```

```bash
oci iam tag list-cost-tracking --compartment-id "$TENANCY_ID" --limit 50 --query 'data[].name'
```

</details>

<details><summary><strong>oci-terraform</strong></summary>

[Open skill](../skills/oci-terraform/SKILL.md)

**Use when:** terraform, opentofu, provider `oracle/oci`, terraform plan or import, resource discovery, adopt existing infra, remote state, ORM stack, `create-plan-job`, drift, `oracle.oci` Ansible inventory.

**Not for:** what the code creates — route the resource question to that service's skill.

```bash
oci resource-manager stack list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data[].{id:id,version:"terraform-version"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci resource-manager job list --stack-id "$STACK_ID" --limit 20 --query 'data[].{id:id,operation:operation,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci resource-manager job get --job-id "$JOB_ID" --query 'data.{id:id,operation:operation,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

</details>

<details><summary><strong>oci-vault-certificates</strong></summary>

[Open skill](../skills/oci-vault-certificates/SKILL.md)

**Use when:** vault, KMS, master encryption key, secret version or stage, rotate a key, "`--endpoint` is required", certificate expiring, mTLS cert, customer-managed key, HSM vs software, segredo, cofre.

**Not for:** OS or database credentials (`oracle-db-sql-access`) or CI auth (`oci-devops-pipelines`).

```bash
oci kms management vault list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data[].{id:id,management:"management-endpoint",state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci kms management key list --compartment-id "$COMPARTMENT_ID" --endpoint "$MGMT_ENDPOINT" --limit 20 --query 'data[].{id:id,mode:"protection-mode",state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci vault secret list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data[].{id:id,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

</details>

<details><summary><strong>oracle-apex</strong></summary>

[Open skill](../skills/oracle-apex/SKILL.md)

**Use when:** APEX, Application Express, `f100.sql`, apex export or import, workspace, ORDS module, AutoREST, APEX Assistant, `APEX_AI` provider, Universal Theme, upgrade status, drift between environments, exportar aplicação APEX.

**Not for:** raw SQL access for an agent (`oracle-db-sql-access`) or ADB provisioning (`oracle-autonomous-db`).

```bash
oci db autonomous-database list --compartment-id "$COMPARTMENT_ID" --limit 10 --query 'data[].{id:id,workload:"db-workload",state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci db autonomous-database get --autonomous-database-id "$ADB_ID" --query 'data."apex-details"' --profile "$PROFILE" --region "$REGION"
```

```bash
oci db autonomous-database get --autonomous-database-id "$ADB_ID" --query 'data."connection-urls".{apex:"apex-url",ords:"ords-url"}' --profile "$PROFILE" --region "$REGION"
```

</details>

<details><summary><strong>oracle-autonomous-db</strong></summary>

[Open skill](../skills/oracle-autonomous-db/SKILL.md)

**Use when:** autonomous database, ADB, ATP, ADW, always free database, wallet, mTLS vs TLS, tnsnames, ACL, ORA-12506, "the database is stopped", `_low`/`_medium` service, python-oracledb, banco autônomo.

**Not for:** Base DB or Exadata (`oracle-db-fleet`), vectors (`oracle-db-vector-ai`), agent SQL access (`oracle-db-sql-access`).

```bash
oci db autonomous-database list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data[].{id:id,state:"lifecycle-state",version:"db-version",free:"is-free-tier"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci db autonomous-database get --autonomous-database-id "$ADB_ID" --query 'data.{state:"lifecycle-state",mtls:"is-mtls-connection-required",acl:"whitelisted-ips"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci db autonomous-db-version list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data[].{version:version,workload:"db-workload"}' --profile "$PROFILE" --region "$REGION"
```

</details>

<details><summary><strong>oracle-db-fleet</strong></summary>

[Open skill](../skills/oracle-db-fleet/SKILL.md)

**Use when:** Base DB, Exadata noun sets, HeatWave, OCI PostgreSQL, multicloud DB, managed RAC/Data Guard/AWR/PDB/RMAN, Ops Insights.

**Not for:** Autonomous (`oracle-autonomous-db`) or standalone engine troubleshooting without OCI management.

```bash
oci db system list --compartment-id "$COMPARTMENT_ID" --limit 10 --query 'data[].{id:id,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci db cloud-exa-infra list --compartment-id "$COMPARTMENT_ID" --limit 10 --query 'data[].{id:id,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci mysql db-system list --compartment-id "$COMPARTMENT_ID" --limit 10 --query 'data[].{id:id,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

</details>

<details><summary><strong>oracle-db-sql-access</strong></summary>

[Open skill](../skills/oracle-db-sql-access/SKILL.md)

**Use when:** SQLcl MCP, `sql -mcp`, database MCP, "run this SQL from the agent", ORDS endpoint, usuário somente leitura.

**Not for:** schema design or vectors (`oracle-db-vector-ai`).

```bash
oci dbtools connection list --compartment-id "$COMPARTMENT_ID" --limit 10 --query 'data.items[].{id:id,state:"lifecycle-state",type:type}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci dbtools connection get --connection-id "$CONNECTION_ID" --query 'data.{id:id,state:"lifecycle-state",type:type}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci dbtools private-endpoint list --compartment-id "$COMPARTMENT_ID" --limit 10 --query 'data.items[].{id:id,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

</details>

<details><summary><strong>oracle-db-vector-ai</strong></summary>

[Open skill](../skills/oracle-db-vector-ai/SKILL.md)

**Use when:** VECTOR column, `VECTOR_DISTANCE`, HNSW, IVF, embeddings in the database, `DBMS_VECTOR`, chunking, hybrid search, RAG on Oracle, Select AI, NL2SQL, busca semântica no banco.

**Not for:** the OCI Generative AI inference endpoint outside the database (`oci-generative-ai`).

```bash
oci db autonomous-database list --compartment-id "$COMPARTMENT_ID" --limit 10 --query 'data[].{id:id,version:"db-version"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci db autonomous-database get --autonomous-database-id "$ADB_ID" --query 'data.{version:"db-version",state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci db autonomous-db-version list --compartment-id "$COMPARTMENT_ID" --limit 10 --query 'data[].version' --profile "$PROFILE" --region "$REGION"
```

</details>

<details><summary><strong>oracle-enterprise-apps</strong></summary>

[Open skill](../skills/oracle-enterprise-apps/SKILL.md)

**Use when:** Fusion/NetSuite/OIC/OAC/ODA/Visual Builder/WebLogic service scope, environment inventory, which application objects the OCI CLI can reach.

**Not for:** application UI authoring, business transactions, CLI spelling errors (`oci-navigator`) or core OCI operations.

```bash
oci fusion-apps fusion-environment list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data.items[].{id:id,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci integration integration-instance list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data[].{id:id,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci analytics analytics-instance list --compartment-id "$COMPARTMENT_ID" --limit 20 --query 'data[].{id:id,state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

</details>
