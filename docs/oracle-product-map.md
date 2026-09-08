# Oracle product map for cloud engineering

Reviewed 2026-09-08. This is an operational map, not a complete inventory of Oracle's commercial catalog. [`catalog/products.json`](../catalog/products.json) supplies machine-readable routing; the generated CLI catalog measures CLI families and commands, which do not map one-to-one to products. One Database product can expose many CLI groups; APEX application operations can require SQLcl even when its hosting database has OCI APIs.

## Choose the control plane before choosing the tool

| Need | Product boundary | Interface and first decision |
|---|---|---|
| Run a VM, attach storage, connect networks | OCI Compute, Block Volume, VCN | OCI API/CLI/SDK or Terraform; select tenancy, region, compartment, image/shape, subnet and IAM first |
| Run Kubernetes | OKE | OCI manages cluster/node infrastructure; Kubernetes API manages workloads. Decide basic/enhanced and managed/virtual/self-managed nodes from current regional support |
| Run containers without managing a cluster | Container Instances | OCI lifecycle APIs; explicitly plan restart, networking, image retrieval and persistence |
| Execute event-driven application code | Functions, API Gateway, Events | OCI provisioning plus function build/image lifecycle; invocation is application execution and can have side effects |
| Automate infrastructure lifecycle | Terraform OCI provider, Resource Manager | Desired state, import ownership, state storage/locking and reviewed plans; discovery alone does not establish a safe apply |
| Build and deploy code | OCI DevOps, Artifact Registry, OCIR | Build/deploy pipelines versus generic artifacts versus container images; choose runtime target and credential boundary |
| Operate a database fleet | Autonomous AI Database, Base Database, Exadata, MySQL HeatWave | OCI provisioning APIs are separate from SQL/data access; select engine, deployment model and backup responsibilities |
| Build an Oracle database application | APEX, ORDS, SQLcl, language drivers | Workspace/schema/application lifecycle differs from host provisioning; treat schema migrations as data changes |
| Run inference or retrieve enterprise knowledge | OCI Generative AI, Generative AI Agents | Inference, agent control plane and agent runtime have separate endpoints, permissions and cost drivers |
| Deploy Oracle databases alongside another cloud's apps | Database@Azure/@Google Cloud/@AWS | Check partner subscription, regional offering, network reachability, identity and billing; do not infer parity with native OCI |
| Operate Fusion business applications | Fusion ERP/HCM/SCM/CX and their agents | Use the application's supported APIs and authorization model; OCI tenancy IAM alone does not grant business-data access |

The service relationships above follow Oracle's [DevOps guide](https://docs.oracle.com/en-us/iaas/Content/GSG/Reference/getting-started-as-devops.htm), [OKE overview](https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengoverview.htm), [database connection guide](https://docs.oracle.com/en-us/iaas/autonomous-database-serverless/doc/connect-tools.html), and [multicloud architecture guidance](https://docs.oracle.com/en/solutions/oci-best-practices/deploy-multicloud-oci-oracle-database-services1.html). Entries marked `discovery_only` in the catalog are navigation pointers awaiting product-specific verification, not validated integrations.

## Coverage by operational domain

| Domain | Services to include in discovery | What an agent must distinguish |
|---|---|---|
| Compute and containers | Compute, autoscaling, OKE, Container Instances, Functions | Capacity versus quota, CPU architecture, image compatibility, cluster versus workload lifecycle |
| Networking and edge | VCN, subnets, NSGs/security lists, routing, DRG, FastConnect/VPN, LB/NLB, DNS, WAF, Network Firewall | Public endpoint versus allowed route; regional resources versus cross-region links; L7 load balancing versus L4 requirements |
| Storage | Object Storage, Block/boot volumes, File Storage, backups | Object API versus attached block versus NFS; backup/replication is not a demonstrated restore |
| Identity and security | IAM, Identity Domains, Vault/Keys/Secrets, Bastion, Cloud Guard, Security Zones, Data Safe | Cloud IAM versus application/domain identity; key metadata versus secret values; assessment versus enforcement |
| SRE | Monitoring, Logging, Audit, Logging Analytics, APM, Stack Monitoring, Health Checks, Events, Notifications, Service Connector Hub | Metrics queries, log queries and Resource Search have different grammars; metric absence can be wrong scope, not zero usage |
| Data engineering | Streaming, Queue, Data Flow, Data Integration, Data Catalog, GoldenGate | Stream log versus task queue; managed Spark versus integration pipelines; metadata catalog versus replicated data |
| Databases | Autonomous, Base Database, Exadata, MySQL HeatWave, NoSQL, PostgreSQL | Engine compatibility, licensing, extensions, backup model, networking and SQL authentication |
| AI | Generative AI, Generative AI Agents, Data Science, Vision, Language, Speech, Document Understanding | Model catalog and region availability are runtime facts; training/hosting/inference/agent execution differ |
| Platform and enterprise | Integration, Analytics, Visual Builder, Digital Assistant, WebLogic, Java Management, Oracle Linux, GraalVM | Product-specific deployments and versions; application administration is not represented fully by OCI CLI |
| Governance and distributed cloud | Budgets, quotas, tagging, organizations, Marketplace, Dedicated Region, Cloud@Customer, Roving Edge, multicloud | Commercial entitlement and operating model; a Marketplace listing is not proof of license or support |

Use the [OCI documentation entry point](https://docs.oracle.com/en-us/iaas/Content/services.htm) and each product's own documentation to resolve a domain entry. This table is a research taxonomy: individual regional coverage, commercial availability and service limits have not been exhaustively revalidated.

## Database, APEX and agent access

Autonomous connection options include wallet-backed mTLS and supported TLS connections without a wallet. These are different modes: “wallet-less mTLS” is not a synonym for TLS. Check the database network policy, client/driver requirements and selected service connection string before connecting. Use a schema with the needed grants for application work; database ADMIN is not the default identity for an agent. [Oracle connection documentation](https://docs.oracle.com/en-us/iaas/autonomous-database-serverless/doc/connect-tools.html).

Provisioning an Autonomous database does not migrate a schema or an APEX application. Track database creation, schema migrations, APEX export/import, ORDS configuration and application smoke checks as separate deliverables. Application exports and SQL scripts belong in version control; credentials and wallets do not. [APEX administration guide](https://docs.oracle.com/en/database/oracle/application-express/24.2/aeadm/oracle-apex-administration-guide.pdf), [ORDS product documentation](https://www.oracle.com/database/technologies/appdev/rest.html).

Oracle currently describes three database MCP deployment choices: local SQLcl over stdio, managed OCI Database Tools, and an ORDS endpoint. Choose by hosting, transport and identity requirements; inspect each server's exposed tools and database privileges before enabling it. The existence of an MCP transport does not establish read-only access or automatically make arbitrary SQL safe. No database MCP deployment was performed for this map. [Oracle MCP comparison](https://www.oracle.com/mcp/).

Vector search, Select AI and in-database model execution are distinct capabilities. Record the actual database release, deployment edition, model/provider and required privileges before proposing SQL. Captured 26ai announcements in the recovered research are leads for verification; they do not establish that every Autonomous shape/region exposes every announced feature.

## Multicloud and commercial boundaries

Oracle's architecture documentation covers Oracle databases deployed with Azure, AWS and Google Cloud. The practical decision is where application traffic and database traffic travel, who owns the subscription and incident response, and which regional database offering is contracted. Interconnects are separate networking products, not proof that a Database@ offering is available in the same location. [Database deployment choices](https://docs.oracle.com/en/solutions/oci-best-practices/deploy-multicloud-oci-oracle-database-services1.html), [multicloud subscriptions](https://docs.oracle.com/en-us/iaas/Content/multicloud/subscriptions-mc.htm), [interconnect](https://docs.oracle.com/en-us/iaas/Content/multicloud/interconnect.htm).

For a cost decision, retrieve the current region, SKU, meter, currency and usage assumptions, plus support and license terms where relevant. Do not mark an entire architecture “free” because one component has a free allowance. Build runners, logs, artifacts, compute, databases, networking and model calls may introduce independent meters. Current price/limit values are intentionally not asserted by this map. [Official price list](https://www.oracle.com/cloud/price-list/).

## Validation and unfinished research

`docs_reviewed` means the cited public source was read on the review date. `discovery_only` means a product/domain is mapped as a research destination. Neither means the product was provisioned, integration-tested, benchmarked or certified. Exact API/CLI syntax must be checked against the installed version before use.

The original unfinished track 09 requested exhaustive operational recipes, regional/pricing limitations and verified commands across DevOps/OKE/security/data/platform products. This map and [SDK/DevOps guide](sdk-and-devops.md) recover its architecture and operator decisions; exhaustive per-service recipes, managed build specifications, add-on/storage/network matrices and live service-limit validation remain unverified.

Track 10 requested SDK recipes plus a 150–250-leaf certification taxonomy with current exam identifiers. No completed taxonomy was recovered. This package does not claim certification coverage or fabricate exam years/codes. Before adding those, verify the current Oracle University objectives and attach a source/date to every exam mapping.
