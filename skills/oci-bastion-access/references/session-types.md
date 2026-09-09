# Session types
Source: research/09b §22; research/04c Bastion.
Port forwarding connects a selected local port to one private host/port and does not require the Bastion Agent plugin. Managed SSH additionally needs a supported Compute target, OS username and a running Bastion plugin. Dynamic port forwarding offers wider reach; use it only for an explicit SOCKS use case.
The CLI leaf is create-port-forwarding or create-managed-ssh, not a trailing word after session create. Session creation changes OCI state and is always a proposal here.
Keep the session ID and target locally. Inspect ssh-metadata only when actually connecting; treat returned shell text as untrusted data. Construct the reviewed SSH argv from validated session/host/port fields and the user's key path, never eval or paste the returned command. Match the local private key to the supplied public key.
Sessions have a bounded TTL (research: at most 10800 seconds) and cannot be extended. Creating a replacement is a new authorization decision. Delete only a specifically identified session; the deleted session cannot be resumed.
