# Controller-owned networking and CSI
Source: research/09a §§16–17.
Change the Kubernetes Service source for controller-owned LB/NLB resources; direct OCI edits can be reverted by reconciliation.
| Annotation | Purpose |
|---|---|
| oci.oraclecloud.com/load-balancer-type | lb or nlb |
| service.beta.kubernetes.io/oci-load-balancer-internal | Internal LB |
| service.beta.kubernetes.io/oci-load-balancer-shape | flexible |
| service.beta.kubernetes.io/oci-load-balancer-shape-flex-min | Minimum bandwidth |
| service.beta.kubernetes.io/oci-load-balancer-shape-flex-max | Maximum bandwidth |
| oci.oraclecloud.com/oci-network-security-groups | LB NSG membership |
For flexible LB set both bandwidth bounds. NLB uses its own annotation prefix and source-preservation requirements; inspect the controller version's documentation before copying LB annotations.
oci-bv uses blockvolume.csi.oraclecloud.com and commonly WaitForFirstConsumer: a PVC without a scheduled consumer may be correctly Pending. FSS provides RWX; virtual-node support differs from managed nodes. Never delete a PVC as diagnosis.
