#!/usr/bin/env python3
"""Map a normalized inventory to OCI; explicit partial list-price comparisons."""
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from urllib.parse import quote, urlencode
from urllib.request import urlopen
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'scripts'))
from lib.pricing import load_prices
from lib.sanitize import clean

SHAPES={'x86_64':('VM.Standard.E5.Flex',2,126,1049,'B97384','B97385'),
        'arm64':('VM.Standard.A2.Flex',2,78,946,'B109529','B109530')}
QUESTIONS=[
 'Commercial vehicle: PAYG or Universal Credits?', 'Windows, Marketplace, encrypted, >400 GB boot or multi-disk assets?',
 'Which sources fit OCM and which require rebuild?', 'Which workloads need an Arm rebuild?',
 'Largest security rule and group counts?', 'Peak concurrent connections and required network capacity?',
 'IAM statement counts and compartment design?', 'Database engine, edition, version and migration precheck?',
 'IPv4/dual-stack subnet requirements?', 'Who pays one-time source egress and migration overlap?']
AWS_REGIONS={'us-east-1':'US East (N. Virginia)','us-west-2':'US West (Oregon)','eu-west-1':'EU (Ireland)','sa-east-1':'South America (Sao Paulo)'}


def fetch(url):
    with urlopen(url,timeout=25) as r: body=r.read(4_000_001)
    if len(body)>4_000_000: raise ValueError('Public price response too large')
    if body[:2]==b'\x1f\x8b': body=gzip.decompress(body)
    if len(body)>8_000_000: raise ValueError('Expanded price response too large')
    return json.loads(body)


def cpu_shape(row):
    arch=str(row.get('arch','')).lower()
    arch={'x86':'x86_64','amd64':'x86_64','aarch64':'arm64','arm':'arm64'}.get(arch,arch)
    if arch not in SHAPES: raise ValueError('Architecture unknown or unsupported; no guessed x86 mapping')
    shape,ratio,maxcpu,maxmem,cpu,mem=SHAPES[arch]
    vcpu=row.get('vcpu'); memory=row.get('memory_gb');cores=row.get('cores')
    if not isinstance(vcpu,(int,float)) or not isinstance(memory,(int,float)) or vcpu<=0 or memory<=0 or not math.isfinite(vcpu+memory):
        raise ValueError('Missing or invalid CPU/memory inventory')
    ocpu=max(1,math.ceil((cores if cores is not None else vcpu/2) if arch=='x86_64' else vcpu/ratio),math.ceil(memory/64))
    if ocpu>maxcpu or memory>maxmem: raise ValueError('Source exceeds selected flex shape ceiling')
    return dict(shape=shape,ocpus=ocpu,memory_gb=memory,cpu_sku=cpu,memory_sku=mem,architecture=arch)


def volume_target(row):
    size=row.get('size_gb');iops=row.get('iops');thr=row.get('throughput_mbps')
    if not isinstance(size,(float,int)) or not math.isfinite(size) or not 0<size<=32768: raise ValueError('Volume size unknown or above 32 TB limit')
    if any(not isinstance(v,(float,int)) or not math.isfinite(v) or v<0 for v in (iops,thr)): raise ValueError('IOPS/throughput unknown; no unconditional gp3 mapping')
    size=max(50,math.ceil(size))
    # Conservative 10+ VPU table. Lower-cost has separate performance rules.
    for vpu in range(10,121,10):
        if iops<=min(size*(1.5*vpu+45),2500*vpu) and thr<=min(size*(12*vpu+360)/1024,20*vpu+280):
            return dict(size_gb=size,vpu=vpu,multipath_required=vpu>=30)
    raise ValueError('IOPS/throughput exceeds supported VPU envelope; do not clamp')


class SourcePrices:
    def __init__(self,online=False): self.online=online;self.cache={}
    def compute(self,cloud,row):
        if not self.online: return None
        region=row.get('region'); instance=row.get('instance_type')
        if not region or not instance: return None
        try:
            if cloud=='aws' and region in AWS_REGIONS and str(row.get('os','')).lower() in {'linux','linux/unix'}:
                name=AWS_REGIONS[region]
                url='https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/'+quote(name,safe='')+'/Linux/index.json'
                if url not in self.cache: self.cache[url]=fetch(url)
                data=self.cache[url]
                matches=[x for x in data.get('regions',{}).get(name,{}).values() if x.get('Instance Type')==instance]
                rates={str(x['price']) for x in matches if 'price' in x}
                if len(rates)!=1: return None
                return {'hourly':float(rates.pop()),'currency':'USD','source':url,'snapshot':data.get('manifest',{}).get('hawkFilePublicationDate'),'basis':'Linux on-demand'}
            if cloud=='azure' and re.fullmatch(r'[a-z0-9]+',region) and re.fullmatch(r'[A-Za-z0-9_]+',instance):
                query=f"armRegionName eq '{region}' and armSkuName eq '{instance}' and priceType eq 'Consumption'"
                url='https://prices.azure.com/api/retail/prices?'+urlencode({'$filter':query})
                if url not in self.cache:self.cache[url]=fetch(url)
                data=self.cache[url]
                if data.get('NextPageLink'):return None
                windows=str(row.get('os','')).lower()=='windows'
                matches=[x for x in data.get('Items',[]) if x.get('unitOfMeasure')=='1 Hour' and x.get('currencyCode')=='USD'
                  and x.get('meterName')==instance.removeprefix('Standard_').replace('_',' ') and ('Windows' in x.get('productName',''))==windows]
                rates={x['retailPrice'] for x in matches}
                if len(rates)!=1:return None
                return dict(hourly=rates.pop(),currency='USD',source=url,snapshot=matches[0].get('effectiveStartDate'),basis='Consumption; exact meter and OS')
        except Exception: return None
        return None


def assess(inv,book,online=False):
    if inv.get('schema')!='oci-migration-inventory/v1' or not isinstance(inv.get('scope',{}).get('services_not_readable'),list): raise ValueError('Normalized scoped inventory required')
    out=[]; source=SourcePrices(online);cloud=inv['source_cloud'];hours=730
    def amount(sku,q):
        try:return float(book.cost(sku,q))
        except (KeyError,ValueError,StopIteration):return None
    for kind in ('compute','block','object','database','network','lb','k8s','serverless','dns'):
        for i,row in enumerate(inv.get(kind,[])):
            rid=row.get('id') or row.get('name') or f'{kind}-{i}'
            rid=rid if str(rid).startswith('sha256:') else 'sha256:'+hashlib.sha256(str(rid).encode()).hexdigest()[:12]
            line=dict(resource=rid,kind=kind,target=None,oci_monthly=None,source_monthly=None,warnings=[],status='needs customer input')
            try:
                if kind=='compute':
                    target=cpu_shape(row);line['target']=target
                    a,b=amount(target['cpu_sku'],target['ocpus']*hours),amount(target['memory_sku'],target['memory_gb']*hours)
                    line['oci_monthly']=a+b if a is not None and b is not None else None
                    sp=source.compute(cloud,row)
                    if sp:line.update(source_monthly=sp['hourly']*hours,source_price=sp)
                    line['route']='OCM candidate; precheck required' if cloud=='aws' and target['architecture']=='x86_64' and row.get('root_device')=='ebs' else 'rebuild/manual migration; validate architecture and image'
                    if target['architecture']=='arm64':line['warnings'].append('Arm target requires binary/container tests; no automatic OCM Arm rehost')
                    if 'windows' in str(row.get('os','')).lower():line['warnings'].append('Windows license, export and BYOL eligibility unresolved; license uplift excluded')
                    if any(os in str(row.get('os','')).lower() for os in ('rhel','red hat','suse')):line['warnings'].append('Commercial Linux subscription and portability unresolved; license uplift excluded')
                    if str(row.get('state','')).upper() in {'STOPPED','STOPPING','DEALLOCATED'}:line['warnings'].append('Stopped source: 730-hour capacity scenario, not an estimate of its current bill')
                    line['warnings'].append('Shape capacity, performance, connection limits and HA must be validated; 730 hours assumed')
                elif kind=='block':
                    target=volume_target(row);line['target']=target
                    a,b=amount('B91961',target['size_gb']),amount('B91962',target['size_gb']*target['vpu'])
                    line['oci_monthly']=a+b if a is not None and b is not None else None
                    if target['multipath_required']:line['warnings'].append('UHP requires multipath and supported compute shape')
                elif kind=='database':
                    engine=str(row.get('engine','')).lower()
                    target='Base Database; Autonomous requires suitability assessment' if 'oracle' in engine else 'MySQL HeatWave' if engine=='mysql' else 'OCI Database with PostgreSQL' if engine=='postgres' else 'rearchitecture / self-managed / retain source'
                    line['target']=target;line['warnings']+=['Engine/version/edition, extension parity, HA, downtime and licensing need migration prechecks; database price excluded']
                    if engine.startswith('aurora'):line['warnings'].append('Aurora storage has no drop-in OCI equivalent')
                    if engine.startswith('sqlserver'):line['warnings'].append('No managed OCI SQL Server target')
                else:
                    line['target']={'object':'Object Storage','network':'VCN + DRG','lb':'Network Load Balancer' if row.get('kind') in {'nlb','network'} else 'Flexible Load Balancer',
                      'k8s':'OKE','serverless':'OCI Functions (container rebuild)','dns':'OCI DNS'}[kind]
                    line['warnings'].append('Usage, feature parity and shared tenancy allowances unresolved; no price invented')
                if line['oci_monthly'] is not None:line['status']='partial list-price estimate'
            except (ValueError,TypeError) as exc:line['warnings'].append(str(exc))
            out.append(line)
    answers=[]
    for idx,q in enumerate(QUESTIONS,1):
        answer='needs customer input'
        if idx==3:answer='; '.join(sorted({r['route'] for r in out if r.get('route')})) or answer
        if idx==4:answer=str(sum('Arm target' in w for r in out for w in r['warnings']))+' Arm candidates; rebuild validation required'
        if idx==8:answer='; '.join(sorted({str(r.get('engine','unknown')) for r in inv.get('database',[])}))+'; editions and migration prechecks need customer input'
        answers.append(dict(question=q,answer=answer))
    priced=[r for r in out if r['oci_monthly'] is not None]
    comparable=[r for r in priced if r['source_monthly'] is not None]
    return dict(schema='oci-migration-report/v1',synthetic=inv.get('synthetic',False),currency='USD',hours_per_month=hours,
        price_snapshot=book.snapshot,price_retrieved_at=getattr(book,'retrieved_at',None),basis='list price, pre-discount; not a complete TCO',resources=out,questions=answers,
        coverage=inv['scope'],totals={'oci_priced_subset':round(sum(r['oci_monthly'] for r in priced),2),
        'priced_resources':len(priced),'total_resources':len(out),'comparable_resources':len(comparable),
        'same_subset_source':round(sum(r['source_monthly'] for r in comparable),2) if comparable else None,
        'same_subset_oci':round(sum(r['oci_monthly'] for r in comparable),2) if comparable else None,'full_savings':None},
        exclusions=['Committed discounts and source contracts','Source egress and overlap during migration','Database/license/storage extras',
                    'Network, object requests, load balancer bandwidth, backups, support, HA and operational labor',
                    'GCP live price requires a customer API key/export; absent here'],
        warnings=['Free Tier is not a production capacity or retention guarantee','Multi-AZ topology cannot be replaced by fault domains without an HA review',
                  'Off-cloud backups, tested restore, support escalation and a reversible cutover plan are required',
                  'Confirm regional capacity and quotas before promising deployment'])


def markdown(report):
    t=report['totals'];lines=['# Migration assessment','',
        'SYNTHETIC fixture; no source account read.' if report['synthetic'] else 'Based on supplied source inventory; completeness follows its coverage declaration.',
        f"USD list price, pre-discount; snapshot {report['price_snapshot']}; 730 hours/month.",
        f"Priced subset: {t['priced_resources']}/{t['total_resources']} resources, USD {t['oci_priced_subset']:.2f}/month. Full-estate saving: unknown.",'',
        '| Kind | Resource | OCI target | Source scenario USD/month | OCI subset USD/month |','|---|---|---|---:|---:|']
    for r in report['resources']:
        target=r['target'];label=target.get('shape',f"Block volume {target.get('vpu')} VPU") if isinstance(target,dict) else target
        lines.append(f"| {r['kind']} | {r['resource']} | {label or 'needs input'} | {round(r['source_monthly'],2) if r['source_monthly'] is not None else 'unknown'} | {round(r['oci_monthly'],2) if r['oci_monthly'] is not None else 'unknown'} |")
    lines+=['',f"Comparable subset: {t['comparable_resources']} resources; source USD {t['same_subset_source']}, OCI USD {t['same_subset_oci']}. These are 730-hour capacity scenarios, not current bills.",
            '', '## Coverage and price provenance', '', 'Regions scanned: '+', '.join(report['coverage'].get('regions_scanned',[])),
            'Services not readable: '+', '.join(report['coverage'].get('services_not_readable',[])),
            'OCI retrieval: '+str(report.get('price_retrieved_at'))]
    for source in {r['source_price']['source']:r['source_price'] for r in report['resources'] if r.get('source_price')}.values():
        lines.append(f"- [{source['basis']}]({source['source']}); snapshot {source['snapshot']}.")
    lines+=['','## Assessment questions','']+['- '+q['question']+' '+q['answer'] for q in report['questions']]
    lines+=['','## Exclusions and decisions','']+['- '+w for w in report['exclusions']+report['warnings']]
    lines+=['','## Resource warnings','']+['- '+r['resource']+': '+clean(w)[0] for r in report['resources'] for w in r['warnings']]
    return '\n'.join(lines)+'\n'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('inventory',type=Path);p.add_argument('--price-cache',type=Path)
    p.add_argument('--live-source-prices',action='store_true');p.add_argument('--format',choices=['json','md'],default='md');p.add_argument('--out',type=Path)
    p.add_argument('--json-out',type=Path,help='Save the same assessment as JSON as well')
    a=p.parse_args()
    try:report=assess(json.loads(a.inventory.read_text()),load_prices(a.price_cache),a.live_source_prices)
    except Exception:p.exit(1,'Assessment unavailable: invalid inventory or public price snapshot.\n')
    text=json.dumps(report,indent=2)+'\n' if a.format=='json' else markdown(report)
    if a.json_out:a.json_out.write_text(json.dumps(report,indent=2)+'\n')
    if a.out:a.out.write_text(text)
    else:print(text,end='')


if __name__=='__main__': main()
