# Launch and resize
Source: research/04c Compute.
Before proposing launch, identify compartment, AD, compatible image, subnet, shape bounds and SSH public-key file. Prefer private placement unless public ingress is requested. CLI user-data-file performs base64 encoding; do not pre-encode or duplicate ssh_authorized_keys in metadata.
Keep the returned instance ID locally for recovery. Termination is irreversible; preserving the boot volume still incurs storage cost.
For resize, capture current shape/configuration, confirm target image compatibility and budget downtime. Record the former configuration for reversal; physical capacity can prevent returning to it. Preserve important data before a separately authorized change.
