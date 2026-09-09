# Oracle Cloud VMware Solution

OCVS provisions VMware SDDCs and bare-metal ESXi hosts. OCI inventory describes the infrastructure envelope; vCenter/NSX and guest workloads have separate credentials, APIs, version matrices and operational responsibilities.
Before lift-and-shift, inventory networking, IP overlap, routing/DNS, storage, host capacity, supported versions and migration tooling. Size from measured workload demand and headroom, not VM count. Validate licensing/support and current regional capacity before a cost or compatibility commitment.
Patching ESXi/vCenter, replacing hosts, scaling clusters and initiating migration are mutations. Drain and maintenance-mode behavior must preserve capacity and application dependencies. OCI lifecycle success does not prove guest or VMware health.
A recovery plan needs configuration backups, data protection, management access and a supported version rollback path. Do not expose vCenter passwords or token-bearing links in reports. This handoff inspects only SDDC metadata.
