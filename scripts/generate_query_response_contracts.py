#!/usr/bin/env python3
"""Generate offline OCI response-field contracts using the installed pinned CLI/SDK.

No OCI credentials or service calls. The object-list CLI response has an explicit
adapter because it differs from the SDK ListObjects envelope. Other mappings
use documented SDK return models; this is not an account response capture.
"""
import argparse, hashlib, importlib, inspect, json, re
from pathlib import Path
import oci
from oci_cli import cli_util, version

def main():
    specs = '''
    audit event list|audit|AuditClient|list_events
    bastion session list|bastion|BastionClient|list_sessions
    budgets budget budget list|budget|BudgetClient|list_budgets
    bv boot-volume-backup list|core|BlockstorageClient|list_boot_volume_backups
    bv volume list|core|BlockstorageClient|list_volumes
    ce cluster list|container_engine|ContainerEngineClient|list_clusters
    ce node-pool list|container_engine|ContainerEngineClient|list_node_pools
    cloud-guard problem list|cloud_guard|CloudGuardClient|list_problems
    compute instance list|core|ComputeClient|list_instances
    compute shape list|core|ComputeClient|list_shapes
    db autonomous-database list|database|DatabaseClient|list_autonomous_databases
    fs file-system list|file_storage|FileStorageClient|list_file_systems
    iam compartment list|identity|IdentityClient|list_compartments
    iam dynamic-group list|identity|IdentityClient|list_dynamic_groups
    iam policy list|identity|IdentityClient|list_policies
    iam user get|identity|IdentityClient|get_user
    kms management vault list|key_management|KmsVaultClient|list_vaults
    limits resource-availability get|limits|LimitsClient|get_resource_availability
    limits value list|limits|LimitsClient|list_limit_values
    logging log-group list|logging|LoggingManagementClient|list_log_groups
    logging-search search-logs|loggingsearch|LogSearchClient|search_logs
    monitoring alarm list|monitoring|MonitoringClient|list_alarms
    monitoring metric-data summarize-metrics-data|monitoring|MonitoringClient|summarize_metrics_data
    network nsg rules list|core|VirtualNetworkClient|list_network_security_group_security_rules
    network route-table list|core|VirtualNetworkClient|list_route_tables
    network security-list list|core|VirtualNetworkClient|list_security_lists
    os bucket get|object_storage|ObjectStorageClient|get_bucket
    os bucket list|object_storage|ObjectStorageClient|list_buckets
    os object list|object_storage|ObjectStorageClient|list_objects
    os object-lifecycle-policy get|object_storage|ObjectStorageClient|get_object_lifecycle_policy
    resource-manager job list|resource_manager|ResourceManagerClient|list_jobs
    search resource structured-search|resource_search|ResourceSearchClient|search_resources
    usage-api usage-summary request-summarized-usages|usage_api|UsageapiClient|request_summarized_usages
    work-requests work-request list|work_requests|WorkRequestClient|list_work_requests
    '''
    primitive={'str':'string','int':'number','float':'number','bool':'boolean','datetime':'string','date':'string'}
    source={}
    def schema(typ,models,seen=()):
        if typ in primitive: return {'type':primitive[typ]}
        if typ.startswith('list['):return {'type':'array','items':schema(typ[5:-1],models,seen)}
        if typ.startswith('dict('):return {'type':'object','properties':{},'additionalProperties':{}}
        if typ in seen or len(seen)>8 or not hasattr(models,typ): return {}
        cls=getattr(models,typ); obj=cls()
        file=Path(inspect.getfile(cls)); source[cls.__module__]=hashlib.sha256(file.read_bytes()).hexdigest()
        serialized=cli_util.to_dict(obj)
        fields={k.replace('_','-'):schema(v,models,(*seen,typ)) for k,v in obj.swagger_types.items()}
        assert set(fields)==set(serialized), (typ, set(fields)^set(serialized))
        return {'type':'object','properties':fields,'additionalProperties':False}
    contracts={}
    for line in specs.strip().splitlines():
        path,module,client,method=line.strip().split('|'); mod=getattr(oci,module); fn=getattr(getattr(mod,client),method)
        match=re.search(r'data of type (list of )?:class:`~(oci\.[^`]+)`',fn.__doc__)
        if not match:raise ValueError((path,fn.__doc__[-1500:]))
        qualified=match[2]; models=importlib.import_module(qualified.rsplit('.',1)[0]); typ=qualified.rsplit('.',1)[1]
        response=schema(typ,models)
        if match[1]:response={'type':'array','items':response}
        contracts[path]={'sdk_method':f'oci.{module}.{client}.{method}','sdk_return':('list of ' if match[1] else '')+qualified,'response':{'type':'object','properties':{'data':response},'additionalProperties':False}}
    models=oci.core.models
    contracts['compute instance list-vnics']={'sdk_method':'Composite CLI read; Vnic result objects','sdk_return':'list of oci.core.models.Vnic','response':{'type':'object','properties':{'data':{'type':'array','items':schema('Vnic',models)}},'additionalProperties':False}}
    # Object-list CLI flattens SDK ListObjects.objects into data and emits sibling metadata.
    contracts['os object list']['response']={'type':'object','properties':{'data':{'type':'array','items':schema('ObjectSummary',oci.object_storage.models)},'prefixes':{'type':'array','items':{'type':'string'}},'next-start-with':{'type':'string'}},'additionalProperties':False}
    contracts['os object list']['cli_adapter']='objectstorage_cli_extended.object_list: render(all_objects, metadata, ctx, display_all_headers=True)'
    record={'format_version':1,'sdk_version':oci.__version__,'cli_version':version.__version__,'scope':'SDK response fields converted by the installed CLI serializer. Command-to-SDK mappings are reviewed; composite list-vnics uses Vnic objects. Unknown/dynamic or recursive shapes remain unverified. No service request or response is generated.','model_source_sha256':source,'contracts':contracts}
    from oci_cli import dynamic_loader
    record['cli_source_sha256'] = {
        'oci_cli.cli_util': hashlib.sha256(Path(inspect.getfile(cli_util)).read_bytes()).hexdigest(),
        'objectstorage_cli_extended.py': hashlib.sha256((Path(dynamic_loader.services_dir)/'object_storage/src/oci_cli_object_storage/objectstorage_cli_extended.py').read_bytes()).hexdigest()}
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    p=Path(__file__).resolve().parents[1]/'evals/query-response-contracts.json'
    rendered=json.dumps(record,indent=2,sort_keys=True)+'\n'
    if args.check:
        if not p.is_file() or p.read_text()!=rendered: raise SystemExit('Query response contracts changed')
        print('35 query response contracts match the installed CLI/SDK')
    else:
        p.write_text(rendered)
        print('35 query response contracts generated')

if __name__ == "__main__":
    main()
