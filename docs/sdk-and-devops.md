# SDK, IaC and DevOps operating guide

Public documentation reviewed 2026-09-08; no pipeline deployment, Terraform apply or application invocation was performed for this guide. The original research scratchpad supplied source leads, and current official documentation was used to check the central decisions below.

## Pick an automation surface

| Surface | Use it for | State and verification |
|---|---|---|
| OCI CLI | Scoped inspection and explicit operational commands | Verify command help, pagination, profile/region and result; there is no universal dry-run |
| OCI SDK | Reusable application/automation logic, structured errors, pagination | Pin package version, choose signer explicitly and bound retries/concurrency |
| Terraform OCI provider | Desired infrastructure with reviewed change plans | Pin provider, keep lockfile, assign state ownership and inspect replacement/deletion |
| Resource Manager | Managed Terraform stacks, state and jobs | Check supported Terraform engine and inspect plan/job logs before apply |
| Ansible `oracle.oci` | Configuration and infrastructure automation in playbooks | Check the collection/module version and idempotency/check-mode support per module |
| SQLcl and database drivers | Schema/application migrations and SQL access | Separate database identity, transactions, grants and rollback from OCI IAM |

Oracle lists SDKs for Java, Python, TypeScript/JavaScript, .NET, Go and Ruby, plus a PL/SQL SDK. PowerShell scripts can invoke the CLI, but this source does not establish a separate first-party OCI PowerShell SDK. [Official SDK index](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdks.htm). The [DevOps guide](https://docs.oracle.com/en-us/iaas/Content/GSG/Reference/getting-started-as-devops.htm) explains Terraform, Ansible and the managed delivery services.

## Authentication is selected by runtime

| Runtime | Preferred pattern to evaluate | Boundary |
|---|---|---|
| Developer workstation | Named OCI profile; API key or supported session-token signer | `from_file` configuration alone is not a generic token refresh mechanism |
| OCI Compute runner | Instance principal with scoped dynamic-group policies | Any process able to use that principal shares its granted authority |
| Supported OCI managed service | Resource principal | SDK must run inside the supported environment with its provided identity |
| OKE workload | OKE workload identity where supported | Cluster/service account and policy conditions matter; it is not interchangeable with a local API key |
| External CI runner | Explicitly documented federation flow, otherwise protected scoped credentials | Do not assume a GitHub OIDC token is accepted by ordinary OCI CLI API-key auth |

Each SDK has its own signer/authentication API; confirm it in the [SDK documentation](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdks.htm) and [configuration guide](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm). CLI-specific environment variables are not automatically SDK configuration. Avoid storing key material or token values in generated code, traces or build artifacts.

## Python: a bounded read-only inventory pattern

Illustrative example using public SDK interfaces; it has not been executed against a tenancy as part of this guide. Offline validation with installed OCI Python SDK 2.185.0 confirmed Python syntax, retry-builder construction and the pagination helper's presence. It deliberately reads one caller-selected compartment. Inventorying a tenancy requires explicit compartment traversal and reporting unreadable scopes.

```python
import os
import oci

config = oci.config.from_file(profile_name=os.environ.get("OCI_PROFILE", "DEFAULT"))
oci.config.validate_config(config)
compartment_id = os.environ["OCI_COMPARTMENT_ID"]
retry = oci.retry.RetryStrategyBuilder(
    max_attempts_check=True, max_attempts=3,
    total_elapsed_time_check=True, total_elapsed_time_seconds=30,
).get_retry_strategy()
compute = oci.core.ComputeClient(config, timeout=(10, 30))
try:
    # Generator avoids eagerly retaining the entire inventory.
    pages = oci.pagination.list_call_get_all_results_generator(
        compute.list_instances, "response", compartment_id=compartment_id,
        retry_strategy=retry,
    )
    for response in pages:
        print({"request_id": response.headers.get("opc-request-id"),
               "instances": [{"id": x.id, "state": x.lifecycle_state}
                             for x in response.data]})
except oci.exceptions.ServiceError as exc:
    print({"status": exc.status, "code": exc.code,
           "request_id": exc.request_id})
    raise
```

The retry elapsed budget applies to an individual API operation; it is not a global timeout for all pages. Large inventories need an overall deadline, page/row budget and cancellation. Do not treat a page size as a complete-result limit. OCI Python supplies eager and lazy pagination helpers; the latter can return models or full responses. [Pagination](https://docs.oracle.com/en-us/iaas/tools/python/latest/pagination.html).

Retry defaults differ by operation; explicitly select a bounded strategy for a workflow. Use backoff/jitter for transient failures, and do not endlessly retry permission failures or assume retries are safe for arbitrary writes. Where a write API supports a retry token, preserve the token for a retry of the same intended operation. Retain `opc-request-id` for diagnosis, while redacting request bodies and credentials. [Python retries](https://docs.oracle.com/en-us/iaas/tools/python/latest/sdk_behaviors/retries.html), [REST API behavior](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/usingapi.htm).

| SDK/application concern | Rule |
|---|---|
| TypeScript/JavaScript | Await SDK requests and page iterators; set cancellation/deadline handling at the caller boundary |
| Go | Pass a bounded context, preserve response metadata and follow each operation's paging contract |
| Java | Configure retry at the appropriate SDK/client/request level, and close clients; do not copy Python option names |
| .NET/Ruby/PL/SQL | Use their documented configuration and paging APIs; keep language-specific examples independently validated |
| Eventual consistency | Poll a documented lifecycle/read operation with a deadline; distinguish accepted, completed and application healthy |
| Errors | An inaccessible/not-found response does not alone prove deletion; inspect scope, identity, region and permissions |

These language rows are implementation guidance, not executed examples. Java's configuration levels are described in [SDK concepts](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/javasdkconcepts.htm); the remaining SDK entry points are in the official index above.

## IaC: adopt resources without losing ownership

Resource Discovery exports supported existing resources from a compartment into configuration and optionally state. It is a starting point for adoption, not a migration guarantee. Inspect generated relationships, unsupported resources, imported identifiers and planned replacements before assigning ownership. Record discovery scope and errors so an incomplete export cannot be mistaken for an empty tenancy. [Current Resource Discovery documentation](https://docs.oracle.com/en-us/iaas/Content/dev/terraform/resource-discovery.htm).

A reviewed lifecycle is: identify existing ownership → pin Terraform/provider versions → import/discover to a separate working directory → inspect configuration and state → validate → plan → review the exact plan → apply within authorized scope → verify resource and application health. Protect state as potentially sensitive; never publish it in research reports. OpenTofu, Pulumi and Crossplane compatibility must be checked for the actual provider/release and required resources rather than inferred from Terraform compatibility.

Resource Manager manages stacks, plans, applies, state and logs; the local Terraform/provider version and managed Terraform runtime are different constraints. The current version page lists 1.5.x/CLI 1.5.7 and says new stacks/jobs below 1.5.x stopped being allowed on 2026-04-30. Confirm the service-reported versions for the target before selecting an engine, especially when reusing older examples. [Resource Manager overview](https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Concepts/resourcemanager.htm), [supported versions](https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Reference/terraformversions.htm).

Do not paste an S3-compatible Terraform backend recipe without checking the Terraform release, OCI endpoint, credential type and locking semantics. Prefer an existing team's supported state backend or Resource Manager. A backend that stores state successfully has not necessarily demonstrated concurrency safety or recovery.

## CI/CD: separate build identity from deployed identity

OCI DevOps provides build and deployment pipelines. A project combines the resources used for delivery; source repositories or external sources feed builds, artifacts feed deployment stages, and runtime environments include Compute, OKE and Functions. Use immutable artifact identifiers/digests in release records and make the deployed version observable. [Service overview](https://docs.oracle.com/en-us/iaas/Content/devops/using/home.htm), [getting started](https://docs.oracle.com/en-us/iaas/Content/devops/using/getting_started.htm).

| Stage | Required design choice | Evidence before advancing |
|---|---|---|
| Source | Repository/ref and trust boundary for untrusted pull requests | Exact commit and resolved dependencies |
| Build | Managed runner, network egress, build spec and temporary secret access | Tests, build logs, dependency/artifact metadata |
| Publish | Generic Artifact Registry versus OCIR container repository | Artifact digest/version and access policy |
| Deploy | Compute, OKE or Functions; rollout strategy and approval policy | Exact target, release artifact, plan and rollback procedure |
| Verify | Infrastructure readiness plus application-level health | Probes and telemetry from the intended endpoint |
| Roll back | Artifact rollback versus schema/data rollback | Tested compatibility; do not assume switching an image undoes a migration |

OCI-hosted pipelines are useful when delivery targets and operational controls live in OCI. Existing GitHub/GitLab pipelines can remain the orchestrator if they meet the same identity, artifact and verification requirements. Federation details, build-runner limits, available images, full build-spec examples and current prices were not independently integration-tested here; do not claim “API-key only,” “all OIDC works,” or “DevOps is entirely free.”

For OKE, verify the cluster context before `kubectl`, and distinguish OCI node-pool/cluster work requests from pod rollout health. Workload identity, ingress, CSI volumes and add-ons each need their own support/permission check. A kubeconfig is an access artifact, not proof a workload can reach its database or pull its image. [OKE overview](https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengoverview.htm).

## Recipes still requiring focused validation

The recovered track 10 requested object multipart uploads/PARs, GenAI chat/embeddings/streaming, agent runtime, Kafka-compatible Streaming, Queue, Vault retrieval, custom metrics/log ingestion, Functions, Events, Notifications and Email Delivery. Those are not interchangeable SDK calls: secrets retrieval exposes sensitive data; object uploads and telemetry ingestion write data; publishing/invoking can trigger downstream actions and charges. Add each recipe only with its service-specific endpoint, signer, permissions, bounded retry policy and meaningful validation.

The requested 150–250-leaf certification taxonomy was not completed in the Claude session. Current exam codes/years, detailed objectives and certification mappings remain unverified. Neither this guide nor the product map claims those deliverables are complete.
