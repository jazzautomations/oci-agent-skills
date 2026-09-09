# Cluster and worker planning
Source: research/09a §§12–13.
Read limits, cluster-options and node-pool-options in the chosen region. Select a supported Kubernetes version deliberately; array order is not a stability guarantee. Match worker image architecture and Kubernetes version to the node pool.
Declare BASIC_CLUSTER or ENHANCED_CLUSTER explicitly. Enhanced features include workload identity and virtual nodes; basic-to-enhanced conversion is not reversible. Quote current cost through oci-cost-analysis before selecting enhanced.
Plan API, worker, pod and LB subnets together. VCN-native pod addressing consumes subnet IPs per pod; capacity is more than a node count. A create response/work request is not a ready cluster. [unverified] Complex node placement/CNI JSON from research has never been applied here; generate and review the installed parameter shape before a proposal.
