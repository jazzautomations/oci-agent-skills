---
name: oci-security
description: Review and remediate defensive OCI posture, IAM exposure, encryption, Cloud Guard, Bastion, Data Safe and network controls.
---

Read [the operator contract](../../docs/operations.md). Identify the authorized
resources and desired control objective. Begin with metadata and configuration,
not secret values or customer data. Catalog examples `security-problems`,
`security-secret-metadata` and `security-bastions` support scoped inspection.

```bash
oci cloud-guard problem list --help
oci vault secret list --help
oci bastion bastion list --help
oci vulnerability-scanning host scan target list --help
```

Distinguish a detected problem, a configured policy and an enforced control. Review
Cloud Guard coverage/targets, Security Zone placement, key/secret lifecycle,
public-access configuration and IAM relationships. No findings can reflect missing
coverage, permissions or delay. A clean scan is not a compliance certification.

For hardening, show the current setting, concrete risk, proposed diff and recovery
path. Preserve administrative access and service dependencies before changing IAM,
routes, firewalls or key permissions. Rotate credentials only with identified
consumers and rollout sequencing; never revoke an active key as a test.

Bastion/SSH work requires explicit target and session scope. Data Safe and database
assessments require the correct database privileges, not only OCI IAM. Share
redacted evidence and exact scope; do not export secrets, raw tenant policy or
customer logs into public audit artifacts.

[Cloud Guard](https://docs.oracle.com/en-us/iaas/cloud-guard/home.htm),
[OCI security](https://docs.oracle.com/en-us/iaas/Content/Security/Concepts/security_guide.htm)
