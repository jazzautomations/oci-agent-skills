#!/usr/bin/env python3
"""Normalize an explicit source-cloud JSON export; performs no cloud calls."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

KINDS=('compute','block','object','database','network','lb','k8s','serverless','dns')


def identity(value):
    value=str(value)
    return value if value.startswith('sha256:') else 'sha256:'+hashlib.sha256(value.encode()).hexdigest()[:12]


def validate(data):
    if data.get('schema')!='oci-migration-inventory/v1' or data.get('source_cloud') not in {'aws','gcp','azure'}:
        raise ValueError('Unknown inventory schema/cloud')
    scope=data.get('scope') or {}
    for key in ('regions_scanned','services_not_readable'):
        if not isinstance(scope.get(key),list): raise ValueError('Missing scope coverage')
    if not scope['regions_scanned']: raise ValueError('No regions scanned')
    for kind in KINDS:
        if kind in data and (not isinstance(data[kind],list) or any(not isinstance(r,dict) for r in data[kind])):
            raise ValueError('Invalid resource collection')
    return data


def redact(data):
    """Drop arbitrary text/tags; hash identifiers. Keep only assessment fields."""
    allowed={'id','name','region','az','instance_type','vcpu','cores','threads_per_core','memory_gb','arch','os','license','state','root_device',
       'vpc_id','subnet_id','network_id','observed','cpu_p95','mem_p95','source','attached_to','size_gb','type','iops','throughput_mbps',
       'encrypted','class','versioning','engine','version','instance_class','storage_gb','multi_az','license_model','cluster_id','cidr','cidrs',
       'subnets','public','nat_gateways','peerings','kind','scheme','listeners','targets','node_groups','count','runtime','memory_mb',
       'invocations_month','avg_ms','zone','record_count','private','cpu_count','db_subnet','marketplace','security_rule_count','security_group_count'}
    ids={'id','name','attached_to','vpc_id','subnet_id','network_id','cluster_id','zone','targets','peerings'}
    def walk(obj,key=''):
        if isinstance(obj,dict): return {k:walk(v,k) for k,v in obj.items() if k in allowed}
        if isinstance(obj,list): return [walk(v,key) for v in obj]
        if key in ids and obj is not None: return identity(obj)
        if isinstance(obj,str): return obj[:160].replace('\n',' ').replace('\r',' ')
        return obj
    result={k:data[k] for k in ('schema','source_cloud','collected_at') if k in data}
    result['synthetic']=bool(data.get('synthetic') or 'synthetic' in str(data.get('note','')).lower())
    result['scope']={'regions_scanned':data['scope']['regions_scanned'],
                     'services_not_readable':list(data['scope']['services_not_readable']),
                     'accounts':[identity(x) for x in data['scope'].get('accounts',[])]}
    for kind in KINDS:
        result[kind]=walk(data.get(kind,[]))
        if kind not in data: result['scope']['services_not_readable'].append(kind+' not exported')
    # Billing exports are never included in public inventory automatically.
    result['cost']={'status':'not imported; supply a separately scoped source price or billing snapshot'}
    return result


def normalize(raw,cloud=None):
    if raw.get('schema')=='oci-migration-inventory/v1': return redact(validate(raw))
    cloud=cloud or raw.get('source_cloud')
    data={'schema':'oci-migration-inventory/v1','source_cloud':cloud,'scope':raw.get('scope'),
          'collected_at':raw.get('collected_at'),'synthetic':bool(raw.get('synthetic'))}
    if cloud=='aws':
        types={t['InstanceType']:t for t in raw.get('instance_types',{}).get('InstanceTypes',[])}
        data['compute']=[]
        for reservation in raw.get('instances',{}).get('Reservations',[]):
            for i in reservation.get('Instances',[]):
                if i.get('State',{}).get('Name')=='terminated': continue
                t=types.get(i.get('InstanceType'),{}); cpu=t.get('VCpuInfo',{}); opts=i.get('CpuOptions',{})
                data['compute'].append(dict(id=i['InstanceId'],instance_type=i.get('InstanceType'),
                    region=i.get('Placement',{}).get('AvailabilityZone','')[:-1],arch=i.get('Architecture'),
                    vcpu=cpu.get('DefaultVCpus'),cores=opts.get('CoreCount',cpu.get('DefaultCores')),
                    threads_per_core=opts.get('ThreadsPerCore',cpu.get('DefaultThreadsPerCore')),
                    memory_gb=t.get('MemoryInfo',{}).get('SizeInMiB',0)/1024 or None,
                    os=i.get('PlatformDetails'),state=i.get('State',{}).get('Name'),root_device=i.get('RootDeviceType'),
                    vpc_id=i.get('VpcId'),subnet_id=i.get('SubnetId')))
        data['block']=[dict(id=v['VolumeId'],size_gb=v.get('Size'),type=v.get('VolumeType'),iops=v.get('Iops'),
            throughput_mbps=v.get('Throughput'),encrypted=v.get('Encrypted'),attached_to=[a.get('InstanceId') for a in v.get('Attachments',[])])
            for v in raw.get('volumes',{}).get('Volumes',[])]
        data['database']=[dict(id=d['DBInstanceIdentifier'],engine=d.get('Engine'),version=d.get('EngineVersion'),
            instance_class=d.get('DBInstanceClass'),storage_gb=d.get('AllocatedStorage'),multi_az=d.get('MultiAZ'),
            license_model=d.get('LicenseModel'),cluster_id=d.get('DBClusterIdentifier')) for d in raw.get('databases',{}).get('DBInstances',[])]
        data['network']=[dict(id=v['VpcId'],cidrs=[v['CidrBlock']],subnets=[dict(id=s['SubnetId'],cidr=s['CidrBlock'],public=s.get('MapPublicIpOnLaunch'))
            for s in raw.get('subnets',{}).get('Subnets',[]) if s.get('VpcId')==v['VpcId']]) for v in raw.get('networks',{}).get('Vpcs',[])]
        data['object']=[dict(name=b['Name'],region=b.get('BucketRegion'),size_gb=None) for b in raw.get('buckets',{}).get('Buckets',[])]
        data['lb']=[dict(id=b['LoadBalancerArn'],kind=b.get('Type'),scheme=b.get('Scheme')) for b in raw.get('load_balancers',{}).get('LoadBalancers',[])]
        expected={'compute':'instances','block':'volumes','database':'databases','network':'networks','object':'buckets','lb':'load_balancers'}
    elif cloud=='gcp':
        data['compute']=[]
        sizes={x['name']:x for x in raw.get('machine_types',[])}
        for i in raw.get('instances',[]):
            t=sizes.get(str(i.get('machineType','')).rsplit('/',1)[-1],{})
            data['compute'].append(dict(id=i['id'],name=i.get('name'),instance_type=t.get('name'),vcpu=t.get('guestCpus'),
               memory_gb=float(t['memoryMb'])/1024 if t.get('memoryMb') else None,arch=t.get('architecture'),
               region=str(i.get('zone','')).rsplit('/',1)[-1].rsplit('-',1)[0],state=i.get('status')))
        data['block']=[dict(id=d['id'],size_gb=float(d['sizeGb']),type=str(d.get('type','')).rsplit('/',1)[-1],
           iops=d.get('provisionedIops'),throughput_mbps=d.get('provisionedThroughput'),attached_to=d.get('users',[])) for d in raw.get('disks',[])]
        expected={'compute':'instances','block':'disks'}
    elif cloud=='azure':
        sizes={x['name']:x for x in raw.get('vm_sizes',[])}
        data['compute']=[]
        for i in raw.get('vms',[]):
            t=sizes.get(i.get('hardwareProfile',{}).get('vmSize'),{})
            data['compute'].append(dict(id=i['id'],name=i.get('name'),region=i.get('location'),instance_type=t.get('name'),
               vcpu=t.get('numberOfCores'),memory_gb=float(t['memoryInMB'])/1024 if t.get('memoryInMB') else None,
               arch=i.get('architecture'),os=i.get('storageProfile',{}).get('osDisk',{}).get('osType')))
        data['block']=[dict(id=d['id'],size_gb=d.get('diskSizeGb'),type=d.get('sku',{}).get('name'),iops=d.get('diskIOPSReadWrite'),
           throughput_mbps=d.get('diskMBpsReadWrite'),attached_to=[d['managedBy']] if d.get('managedBy') else []) for d in raw.get('disks',[])]
        expected={'compute':'vms','block':'disks'}
    else: raise ValueError('Unsupported source cloud')
    validate(data)
    for kind,key in expected.items():
        if key not in raw:
            data.pop(kind,None)
    return redact(data)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input',type=Path);p.add_argument('--cloud',choices=['aws','gcp','azure']);p.add_argument('--out',type=Path)
    a=p.parse_args()
    try: result=normalize(json.loads(a.input.read_text()),a.cloud)
    except (ValueError,TypeError,KeyError): p.exit(1,'Invalid inventory export; explicit scope and source response shapes required.\n')
    text=json.dumps(result,indent=2)+'\n'
    if a.out: a.out.write_text(text)
    else: print(text,end='')


if __name__=='__main__': main()
