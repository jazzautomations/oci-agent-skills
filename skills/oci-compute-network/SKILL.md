---
name: oci-compute-network
description: Operate OCI Compute and networking with explicit capacity, image, VNIC, route, firewall and reachability checks.
---

Read [the operator contract](../../docs/operations.md). Use `oci_instances` and
`oci_network_inventory` for bounded discovery. CLI examples `compute-instances`,
`network-vcns` and `network-subnets` are in
[the example catalog](../../catalog/examples.json).

```bash
oci compute instance list --help
oci compute shape list --help
oci compute image list --help
oci compute instance list-vnics --help
oci network route-table list --help
oci network nsg rules list --help
```

For launch/resize planning, join image architecture and shape compatibility,
availability domain, capacity reservation, service limit and quota. A free-tier
label or nonzero quota is not capacity. Resolve image IDs in the selected region;
never carry an image OCID between regions or assume an old image still exists.

Do not infer that an instance is idle from its name, shape or RUNNING state. Use a
bounded CPU/network/disk history and workload ownership/scheduling evidence before
recommending stop or resize; low CPU alone can hide a stateful or standby service.

For reachability, trace workload → VNIC/subnet → route table → gateway/DRG → peer,
plus the return path. Check NSG and security-list rules, stateful/stateless behavior,
DNS, host firewall and listening process. A public address does not establish an
allowed route or an application listener. LB and NLB health require backend-level
checks; do not widen ingress merely because one health probe fails.

Before network updates, retain the complete current rule/route arrays: many update
APIs replace collections. For reboot/stop/resize/detach, document affected services,
volume persistence and recovery. Verify both OCI lifecycle and application health.
Inspect a work request after ambiguous failure before retrying a mutation.

[Compute](https://docs.oracle.com/en-us/iaas/Content/Compute/home.htm),
[Networking](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/overview.htm)
