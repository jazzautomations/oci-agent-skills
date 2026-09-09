# Provider and authentication
Source: research/08c §§1–2; research/14 §10.
Use the official oracle/oci provider and constrain a reviewed version; commit the dependency lockfile. The research version is a snapshot, not a recommendation to upgrade blindly. Provider upgrades can alter schemas and force replacements.
Choose APIKey, InstancePrincipal, ResourcePrincipal or SecurityToken authentication appropriate to the execution host. A working OCI CLI session does not prove the provider reads the same profile, key passphrase or region. Keep private keys, passwords and tokens out of HCL, tfvars, plans and CI logs.
Use explicit provider aliases for regions and pass them into modules. Root/home-region identity resources and regional infrastructure need deliberate separation. Resource Manager uses its own resource principal; local profile success does not prove stack permissions.
