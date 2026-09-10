# Before moving a workload

| Signal | Required decision |
|---|---|
| GCP/Azure/Arm/instance-store | No OCM rehost assumption; rebuild/manual migration plan |
| Windows/Marketplace/encryption/large multi-disk image | Verify source export license and image limits |
| Multi-AZ source | Check target AD count and cross-region DR; fault domains are not AZs |
| Security rules / many NICs | Check OCI NSG, attachment, conntrack and bandwidth limits |
| Overlapping CIDRs | Allocate non-overlapping target network before hybrid cutover |
| IAM account hierarchy | Design compartment inheritance and policy limits; do not copy AWS IAM JSON |
| Aurora/SQL Server/managed event workflows | Rearchitecture or retain source; price engineering effort |
| PostgreSQL extensions / DB versions | Run engine-specific prechecks and rehearse rollback |
| Oracle BYOL / Windows | Customer licensing evidence required; no automatic compliance claim |
| Dual-stack migration subnet | Verify DMS IPv6 limitations before choosing migration mode |
| Free-tier / capacity unavailable | Production capacity and support cannot be promised from a free account |
| Egress-heavy estate | Separate source one-time export, overlap and recurring target transfer |
| Commitments or credits | Include stranded commitments and actual contracted discounts |
| Data-loss or support incident history | Off-cloud backups, restore test, escalation path, exit plan |
| Untested source services | Report as unread/unknown, exclude from claimed savings |

These warnings are triggers for verification, not claims about every customer.
Practitioner stories in the authoring research are anecdotal and are not outage probabilities.
This tool answers ten assessment questions or explicitly requests customer evidence.

Sources reviewed 2026-09-10:
https://docs.oracle.com/en-us/iaas/Content/cloud-migration/cloud-migration-requirements-specifications.htm
https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/importingcustomimagelinux.htm
https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/overview.htm
