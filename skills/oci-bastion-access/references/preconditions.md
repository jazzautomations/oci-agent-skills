# Access preconditions
Source: research/09b §22; research/04c Bastion.
Confirm the caller's current public egress CIDR is in the bastion allow-list. It is not the target's subnet CIDR. Do not widen the list to the internet to diagnose a failed connection.
Read bastion target subnet, route/security path to the approved target and session lifecycle. For managed SSH, check instance-agent plugin get with instanceagent-id and plugin-name Bastion, plus the target OS username and SSH service.
Distinguish provisioning work-request success from ACTIVE session state. An expired/deleted session or mismatched key can resemble a network failure. A session cannot make an unreachable database listener healthy.
bastion_session.sh only inspects an existing bastion/session and never creates, renews or opens a tunnel. It omits ssh-metadata and secret key content. For VCN redesign route to oci-networking; for guest SSH/cloud-init route to oci-compute.
