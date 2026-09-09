# WebLogic and self-managed runtimes

WebLogic Server for OCI provisioning uses Marketplace and Resource Manager stacks; there is no oci weblogic group. Stack scale/apply and license selection are separate from domain management and need a reviewed Terraform plan and application maintenance scope.
Day-2 WebLogic Management uses wlms and agent-based registration/discovery. An empty domain list means no visible registered domains, not no WebLogic installation. Check agent/plugin state and discovery freshness before concluding absence.
Separate domain lifecycle, managed-server health, deployed application health and patch readiness. OCI lifecycle success does not prove servlet/JDBC/JMS correctness. Configuration and credential reads can disclose passwords; this skill projects only resource IDs and state and does not fetch credential material.
Helidon, Micronaut and Coherence frameworks do not acquire their own OCI CLI groups; route deployment to OKE, Functions or Compute as appropriate. Oracle Linux Automation Manager is self-managed software on hosts, not an OCI control-plane service.
Starting/stopping domains, patching, running host automation and changing Resource Manager stacks are mutations. Gather existing state and failed work-request evidence first. Recovery requires domain/configuration backups and a tested application health gate; no runtime or host action was run here.
