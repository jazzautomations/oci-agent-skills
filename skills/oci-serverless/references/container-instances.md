# Container Instances
Source: research/09a §22.
Container Instances run containers without a Kubernetes cluster. Discover service shapes with list-shapes; Compute VM.Standard names are not valid Container Instance shapes. Choose compatible image architecture, OCPUs/memory and a subnet/AD combination supported in the region.
Container configuration, VNICs, shape-config, health checks, restart policy and registry credentials are structured inputs. [unverified] No complex create payload was applied here; inspect installed parameter JSON and preserve type/units before a proposal.
Private registries require the supported pull credential configuration. Do not emit passwords or resolved secret contents. Confirm service egress, DNS and image digest before interpreting a pull error as application failure.
Restart policy does not provide a multi-node scheduler or a durability guarantee. Treat the container root filesystem as ephemeral; route persistent data requirements to the appropriate storage skill and verify supported mounts. Recreate/restart is a mutation; preserve deployment inputs and data recovery before proposing it.
