---
name: oci-oke
description: Operate Oracle Kubernetes Engine clusters and workloads, separating OCI infrastructure state from Kubernetes rollout and application health.
---

Read [the operator contract](../../docs/operations.md), then the OKE sections of
[the DevOps guide](../../docs/sdk-and-devops.md). CLI examples `oke-clusters` and
`oke-node-pools` are in [the catalog](../../catalog/examples.json).

```bash
oci ce cluster list --help
oci ce node-pool list --help
oci ce cluster create-kubeconfig --help
```

Cluster provisioning uses OCI; deployments/services/RBAC use Kubernetes. Confirm
the actual cluster endpoint and context before any kubectl operation. Generating
kubeconfig writes local access configuration and may need endpoint reachability;
it is not a proof that a workload can reach a database or pull an image.

Inspect cluster/node versions, node model (managed, virtual or self-managed), CNI,
pod/service CIDRs, ingress/LB, DNS, CSI and registry access. Verify support for the
selected model instead of assuming virtual nodes behave like ordinary workers.
Join pending pods with scheduling events, resource requests, storage and quota.
For unreachable services, correlate the last deployment/network diff, then inspect
Service selectors and port/targetPort, EndpointSlices, pod readiness and
NetworkPolicy before the OCI route/NSG/LB path. Use `oci-compute-network` for that
path and `oci-observability` for timed logs/metrics; avoid broad firewall changes.

For delivery, use immutable image digests, readiness probes, bounded rollout,
PodDisruptionBudgets and a documented rollback. Review CRD/schema changes separately
from image rollback. Drain/upgrade changes require spare capacity and disruption
planning. Verify OCI work requests, node readiness, workload rollout and endpoint
health as separate checks.

Use service-account/workload identity where supported with narrow policies. Do not
mount an administrator kubeconfig or tenancy API key into every workload.

[OKE documentation](https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengoverview.htm)
