# DRG, VPN and FastConnect
Source: research/09b §§16–17.
Follow both directions: VCN route to DRG, attachment's DRG route table, imported routes/distributions, destination route, return path. A present attachment alone does not imply transit.
VPN connections have separate tunnel state and routing. Diagnose each tunnel's status, BGP/static routing and CPE configuration. Do not print shared-secret configurations.
FastConnect virtual-circuit lifecycle and BGP session state describe different readiness layers; PENDING_PROVIDER requires partner coordination. Remote peering connects DRGs across regions; a region change requires an explicitly agreed second scope.
Some effective-route operation names in the research were not confirmed individually. Resolve them through catalog help before use; do not invent a get-effective-routes leaf.
