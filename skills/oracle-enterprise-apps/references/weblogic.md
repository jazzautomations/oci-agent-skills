# WebLogic and self-managed runtimes

WebLogic Server for OCI provisioning uses Marketplace and Resource Manager stacks; there is no oci weblogic group. Stack scale/apply and license selection are separate from domain management and need a reviewed Terraform plan and application maintenance scope.
Day-2 WebLogic Management uses wlms and agent-based registration/discovery. An empty domain list means no visible registered domains, not no WebLogic installation. Check agent/plugin state and discovery freshness before concluding absence.
Separate domain lifecycle, managed-server health, deployed application health and patch readiness. OCI lifecycle success does not prove servlet/JDBC/JMS correctness. Configuration and credential reads can disclose passwords; this skill projects only resource IDs and state and does not fetch credential material.
Helidon, Micronaut and Coherence frameworks do not acquire their own OCI CLI groups; route deployment to OKE, Functions or Compute as appropriate. Oracle Linux Automation Manager is self-managed software on hosts, not an OCI control-plane service.
Starting/stopping domains, patching, running host automation and changing Resource Manager stacks are mutations. Gather existing state and failed work-request evidence first. Recovery requires domain/configuration backups and a tested application health gate; no runtime or host action was run here.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| NotFound | Wrong static path / wrong API version / typo'd service endpoint | id 14 [unverified] |
| NotAuthorizedOrNotFound | Deliberate ambiguity: missing resource OR missing policy OR wrong region OR wrong compartment | id 13 [unverified] |
