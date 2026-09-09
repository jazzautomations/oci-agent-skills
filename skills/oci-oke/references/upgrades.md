# Upgrades
Source: research/09a §19.
Inventory control-plane version, node pool versions/images, add-ons, workloads and PodDisruptionBudgets before choosing the next supported version. Upgrade the control plane before workers, respecting supported minor-version steps and skew.
Plan surge capacity, drain grace and rollback limits. Enhanced node cycling and a replacement pool have different recovery behavior; check cluster type first. Preserve the old pool until workloads and storage are healthy.
Control-plane upgrade has no general downgrade rollback. Treat it as an irreversible proposal with a recovery/migration plan. Credential rotation and public-endpoint decommission have separate deadlines and recovery procedures.
