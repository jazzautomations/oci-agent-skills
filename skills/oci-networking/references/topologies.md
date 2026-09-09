# Topology choices
Source: research/13 §5.2, read fully with its staleness caveats.
| Intent | Architecture | Decision |
|---|---|---|
| Shared services across VCNs | hub-spoke-network-drg | DRG tables/distributions support transit |
| Two VCNs, explicit LPG request | hub-spoke-network | Peering is non-transitive |
| CIDR/subnet/gateway layout | oci-network-deployment | Agree addressing before code |
| Design review | oci-best-practices-networking | Review workload tradeoffs |
| Inspection between spokes | cis-oci-benchmark DMZ mode | Symmetric routing through the appliance |
| Cross-region private traffic | DRG remote peering | Explicit second-region scope |
| HA web app | ha-web-app | Use topology; associated stack is archived |
Architecture Center books live at https://docs.oracle.com/en/solutions/ . Use the shared Architecture Center guide for checked links and lookup redirects. Research identifies old terraform-oci-arch stacks as frozen examples, not current deployable defaults; validate release/provider compatibility. A page creation date is not its update date.
