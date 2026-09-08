---
name: oci-devops
description: Build and operate OCI DevOps pipelines, artifact/container delivery, Functions, API Gateway and Container Instances.
---

Read [the operator contract](../../docs/operations.md) and
[SDK/DevOps decisions](../../docs/sdk-and-devops.md). Use catalog examples
`devops-projects`, `devops-artifacts`, `devops-functions` and `devops-containers`.

```bash
oci devops project list --help
oci devops build-pipeline list --help
oci artifacts container repository list --help
oci fn application list --help
oci container-instances container-instance list --help
```

Separate source commit, build identity, artifact digest, deployment target identity
and health verification. OCIR stores container images; Artifact Registry also
handles generic artifacts. Pin release inputs and make the running version observable.

Inspect build-spec/deploy-spec schemas from the current service docs before writing
YAML. Check runner image, CPU architecture, network egress, secret access and target
runtime. External CI federation must follow a documented supported flow; a GitHub
OIDC token is not a drop-in OCI API key. Untrusted PR builds must not inherit release
credentials or deploy authority.

For Functions, distinguish provisioning from building/pushing an image and invoking
the function. Invocation can execute writes and downstream actions. For Container
Instances, plan restart, persistence, image retrieval and observability. For API
Gateway, inspect authentication, backend reachability, timeouts and route matching.

Prepare rollout and rollback for the selected Compute/OKE/Functions target; account
for data migrations separately. A pipeline's success state does not prove endpoint
health. Report billable dependencies and verify current prices rather than labeling
the whole DevOps stack free.

[OCI DevOps](https://docs.oracle.com/en-us/iaas/Content/devops/using/home.htm)
