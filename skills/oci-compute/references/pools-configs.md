# Pools and configurations
Source: research/04c Compute.
Configurations are launch templates; pools select configuration, placement and desired size. Read membership before proposing a scale or configuration change. Changing a template is not evidence that existing instances were replaced.
Capture configuration ID, placement, desired size and autoscaling policy together. Scale-in can terminate members: inspect attached disks, drain requirements and load-balancer membership. Restoring size/configuration cannot restore local ephemeral data.
Oracle Cloud Agent plugins use top-level instance-agent. OS Management Hub enrollment and patch orchestration belong to oci-migration-patching.
