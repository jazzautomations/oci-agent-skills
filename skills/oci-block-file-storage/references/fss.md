# File Storage
Source: research/04c FSS; research/09b §30.
File systems, mount targets, export sets and exports are separate objects. Diagnose mount target placement/IP, export path, client CIDR options, network ports and guest NFS mount configuration in that order.
Set explicit export options, source CIDRs and root squash appropriate to the client. Do not infer permissive defaults from an empty export-options array. Updating options replaces the array; preserve ordering and complete previous options.
Snapshots appear under .snapshot and consume storage. They are not an independent regional backup; a file-system loss can destroy recovery access. Snapshot policy, replication and a tested recovery procedure address different requirements.
Do not run guest mount, growfs, filesystem repairs, attachment or snapshot deletion during read-only diagnosis.
