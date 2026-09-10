# Service mapping (candidate targets, not API compatibility)

Oracle's comparison books provide broad category matches. An equivalent category does not
prove protocol, consistency, engine, quota or operational parity. Rows marked [+] are
assessment additions. Every managed service requires a separate feature precheck.

| # | Domain | AWS | Azure | Google Cloud | OCI | Note |
|---|---|---|---|---|---|---|
| 1 | VM (multi-tenant) | EC2 | Azure Virtual Machines | Compute Engine | Compute VM instances | **[O]** shape mapping in §6 |
| 2 | VM (single-tenant) | EC2 Dedicated Instances | Azure Dedicated Hosts | GCE sole-tenant | Dedicated VM Hosts | **[O]** |
| 3 | Bare metal | EC2 Bare Metal | Azure BareMetal Infrastructure | GCE Bare Metal | BM instances | **[O]** |
| 4 | Kubernetes | EKS | AKS | GKE | **OKE** | **[O]** OKE control plane has a free *Basic* tier |
| 5 | Container registry | ECR | ACR | Artifact Registry | OCI Registry (OCIR) | **[O]** |
| 6 | Serverless functions | Lambda | Azure Functions | Cloud Functions | **OCI Functions** | **[O]** Fn is OCI-Fn/Docker-image based, not zip |
| 9 | Object storage | S3 | Blob Storage | Cloud Storage | Object Storage | **[O]** S3-compat API endpoint exists |
| 10 | Archive tier | S3 Glacier | Blob archive tier | Cloud Storage Nearline | Archive Storage | **[O]** OCI restore is hours, plan for it |
| 11 | Block storage | EBS | Managed Disks | Persistent Disk | Block Volumes | **[O]** perf is a *VPU* setting, not a disk type |
| 12 | Shared file | EFS | Azure Files | Filestore | File Storage (FSS) | **[O]** NFSv3 |
| 13 | Bulk offline transfer | Snowball | Import/Export, Data Box | Transfer Appliance | Data Transfer Appliance / Roving Edge | **[O]** |
| 14 | Hybrid file gateway | Storage Gateway | StorSimple | Storage Transfer Service | **rclone** / OCIFS | **[O]** Oracle's answer is a tool, not a service |
| 15 | Virtual network | VPC | Virtual Network | VPC | **VCN** | **[O]** VCN is regional; subnets can be regional or AD-local |
| 16 | Dedicated interconnect | Direct Connect | ExpressRoute | Cloud Interconnect | FastConnect | **[O]** |
| 17 | Site-to-site VPN | AWS VPN | VPN Gateway | Cloud VPN | VPN Connect | **[O]** free of charge on OCI |
| 18 | DNS | Route 53 | Azure DNS | Cloud DNS | OCI DNS | **[O]** |
| 20 | L7 load balancer | ALB | Application Gateway | Cloud Load Balancing | OCI Load Balancer (flexible) | **[O]** bandwidth is provisioned (min/max Mbps) |
| 21 | L4 load balancer | NLB | Azure Load Balancer | Cloud LB (TCP) | **Network Load Balancer** | **[+]** distinct OCI service from #20 |
| 22 | WAF | AWS WAF | Azure WAF | Cloud Armor | OCI WAF | **[O]** |
| 23 | DDoS | Shield | DDoS Protection | Cloud Armor | OCI DDoS Protection | **[O]** always-on L3/4 at no charge |
| 24 | CDN | CloudFront | Azure CDN / Front Door | Cloud CDN | *(partner: Akamai/CloudFlare)* | **[+]** no native OCI CDN — call it out |
| 25 | Transit hub | Transit Gateway | Virtual WAN | Network Connectivity Center | **DRG** (upgraded) | **[+]** |
| 27 | Managed relational | RDS | Azure SQL Database | Cloud SQL | Base Database / **Autonomous AI TP (ATP)** / **Oracle AI Database@AWS·Azure·GCP** | **[O]** see §3.2 |
| 28 | Cloud-native relational | Aurora | — | AlloyDB | ATP / Oracle AI Database@AWS | **[O]** |
| 29 | Managed MySQL | RDS for MySQL | Database for MySQL | Cloud SQL for MySQL | **MySQL HeatWave** | **[O]** |
| 30 | Managed PostgreSQL | RDS for PostgreSQL | Database for PostgreSQL | Cloud SQL for PostgreSQL | **OCI Database with PostgreSQL** | **[O]** |
| 31 | Cache | ElastiCache | Azure Cache for Redis | Memorystore | **OCI Cache** | **[O]** |
| 33 | NoSQL / KV | DynamoDB | Table Storage, Cosmos DB | Bigtable, Firestore | Oracle NoSQL Database Cloud / Autonomous AI JSON DB | **[O]** |
| 34 | Data warehouse | Redshift | Synapse Analytics | BigQuery | **Autonomous AI Lakehouse** / HeatWave | **[O]** (formerly "Autonomous Data Warehouse") |
| 36 | Streaming ingest | Kinesis | Stream Analytics | Pub/Sub | OCI Streaming | **[O]** Kafka-compatible |
| 37 | Queue | SQS | Queue Storage | Pub/Sub | **OCI Queue** (Azure/GCP books say Streaming) | **[O]** the AWS book's answer, Queue, is the better one |
| 38 | Pub/sub notification | SNS | Service Bus | Pub/Sub | OCI Notifications | **[O]** |
| 39 | Event bus | EventBridge / CloudWatch Events | Event Grid | Cloud Audit Logs | **OCI Events** | **[O]** |
| 43 | ML platform | SageMaker | Azure ML | Vertex / AI Platform | OCI Data Science (+ Data Labeling) | **[O]** |
| 44 | IaC deploy | CloudFormation | ARM / Bicep | Deployment Manager, Cloud Build | **Resource Manager** (Terraform) | **[O]** OCI's native IaC *is* Terraform |
| 45 | Monitoring | CloudWatch | Azure Monitor | Cloud Monitoring | OCI Monitoring | **[O]** |
| 46 | Logging | CloudWatch Logs | Azure Monitor Logs | Cloud Logging | OCI Logging (+ Logging Analytics) | **[O]** |
| 47 | Identity | IAM | Entra ID | Cloud IAM | **OCI IAM + identity domains** | **[O]** and **compartments** — see below |
| 48 | Key management | KMS | Key Vault | Cloud KMS | OCI Vault | **[O]** |
| 49 | Audit trail | CloudTrail | Activity Log | Cloud Audit Logs | OCI Audit | **[O]** 365-day retention, no config needed |
| 50 | Posture / CSPM | Inspector, Security Hub | Defender for Cloud, Sentinel | Security Command Center | **Cloud Guard** (+ Security Zones) | **[O]** |
| 51 | Account grouping | Organizations, Resource Groups | Management Groups, Resource Groups | Folders, Projects | **Compartments** | **[O]** |
| 52 | Tenancy | Account | Subscription | Project | Tenancy | **[O]** |
| 53 | Zone | Availability Zone | Availability Zone | Zone | **Availability Domain** | **[O]** |
| 54 | Rack isolation | Placement group | — | — | **Fault Domain** | **[O]** 3 per AD, free, always use them |


| Failure signal | Action |
|---|---|
| Native mover unavailable | Rebuild/manual migration, or retain source |
| Aurora / SQL Server / proprietary serverless | Rearchitecture, no drop-in promise |

Sources, reviewed 2026-09-10:
https://docs.oracle.com/en/solutions/oci-for-aws-professionals/
https://docs.oracle.com/en/solutions/oci-for-azure-professionals/
https://docs.oracle.com/en/solutions/oci-for-gcp-professionals/
