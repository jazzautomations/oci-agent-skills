# Metric discovery
Source: research/09b §1.
Identify compartment, namespace, metric name, dimensions and time window before writing an alarm. resourceGroup is a separate query parameter, not a dimension. Do not infer metric availability from the existence of the service.
Research observed these eight namespaces in its tenancy-wide sample: oci_autonomous_database, oci_blockstore, oci_compute, oci_compute_infrastructure_health, oci_logging, oci_objectstorage, oci_vcn, oci_vcnip. The current skill's bounded metadata check is narrower; its evidence is not that inventory.
| Namespace candidate | Intended signal |
|---|---|
| oci_computeagent | Guest CPU/memory; agent plugin required |
| oci_compute_infrastructure_health | Infrastructure accessibility |
| oci_blockstore | Volume throughput/IOPS |
| oci_objectstorage | Requests, size and errors |
| oci_vcn | VNIC drops and traffic |
| oci_lbaas | LB backend health |
| oci_autonomous_database | Database CPU/storage/sessions |
| oci_faas | Function execution |
| oci_apigateway | Gateway requests/latency |
| oci_healthchecks | External probe health |
| oci_managementagent | Agent availability |
Candidates absent from research's observed list are [unverified] in this tenancy. Discover exact names, dimensions, units and supported aggregations from emitted metadata; do not assume similar services share a namespace.
Custom metric namespaces cannot use reserved oci_ or oracle_ prefixes. Missing data may reflect IAM, compartment, region, stopped resources, a disabled agent or an incorrect filter, rather than health.
