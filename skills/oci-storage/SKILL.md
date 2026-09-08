---
name: oci-storage
description: Inspect and manage OCI Object, Block, boot and File Storage while preserving retention, backup, encryption and attachment semantics.
---

Read [the operator contract](../../docs/operations.md). Begin with storage type and
data ownership. The bundled `oci_buckets` exposes bucket metadata, not object
contents. CLI examples `storage-namespace` and `storage-volumes` are in
[the catalog](../../catalog/examples.json).

```bash
oci os bucket list --help
oci os object list --help
oci bv volume list --help
oci bv backup list --help
oci bv boot-volume list --help
oci fs file-system list --help
```

Distinguish namespace, bucket name and region. Namespace is tenancy metadata, not a
compartment. Use prefix and a page budget when inspecting object keys; keys can
contain private customer information. Do not download object bodies for metadata
questions. Streams returned by object retrieval are not metadata model objects.

For block/boot volumes, join attachment mode, instance state, encryption key,
backup policy and application consistency. A successful volume backup is not a
tested database restore. File Storage adds mount targets, exports and network
access controls; a filesystem alone is not an accessible NFS mount.

Before retention/lifecycle/versioning changes, enumerate consequences for existing
versions and recovery. Retention locks and deletes may be irreversible. Object
sync can delete destinations; inspect the exact supported preview semantics.
Pre-authenticated requests are bearer access grants: bound scope/expiry, obtain
authorization to expose data and never include their URLs in public output.

[Object Storage](https://docs.oracle.com/en-us/iaas/Content/Object/Concepts/objectstorageoverview.htm),
[Block Volume](https://docs.oracle.com/en-us/iaas/Content/Block/Concepts/overview.htm)
