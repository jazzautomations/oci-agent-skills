# Resource discovery
Source: research/08c §5; research/data/tf-rd-services.json.
tf-rd-services.json is a byte-for-byte snapshot of the 132 service/scope rows collected in research. Count rows, not unique service names: some names appear for both tenancy and compartment scope. It is not proof that every resource in a service is supported.
Choose an explicit region, compartment and service filter. Resource discovery can read broad tenancy data and emit HCL/state containing identifiers and secrets. Keep generated artifacts local and redacted; do not publish them.
Generated code needs provider/version review, reference cleanup, naming, dependency checks and a no-change plan before adoption. Discovery itself is not an import or a safe apply plan. [unverified] No discovery provider execution, plan or apply was performed here.
