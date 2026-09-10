#!/usr/bin/env python3
"""Bounded OCI waste assessment. Reads only; unknown coverage never proves absence."""
import argparse
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'scripts'))
from lib.oci_ro import run
from lib.pricing import load_prices
from lib.costs import rows as cost_rows, utc
from lib.sanitize import clean, emit

SHAPES={'VM.Standard.E5.Flex':('B97384','B97385'),'VM.Standard.E4.Flex':('B93113','B93114'),'VM.Standard.A1.Flex':('B93297','B93298')}
RECIPES={
 'D1':('oci bv volume delete --volume-id "${REVIEWED_VOLUME_ID}"','Irreversible; verify a restorable backup before deletion'),
 'D2':('oci bv boot-volume delete --boot-volume-id "${REVIEWED_BOOT_VOLUME_ID}"','Irreversible; verify a restorable backup before deletion'),
 'D4':('oci bv volume update --volume-id "${REVIEWED_VOLUME_ID}" --vpus-per-gb 10','Restore the recorded original VPU value; verify shape and latency first'),
 'D5':('oci compute instance update --instance-id "${REVIEWED_INSTANCE_ID}" --shape-config "${REVIEWED_SHAPE_CONFIG}"','Restore original shape configuration; schedule reboot and application checks'),
 'D10':('oci os object-lifecycle-policy put --bucket-name "${REVIEWED_BUCKET}" --items "file://${REVIEWED_POLICY_JSON}"','Save original policy; irreversible deletions cannot be rolled back'),
}


def ref(value): return 'sha256:'+hashlib.sha256(str(value).encode()).hexdigest()[:12]


def numeric(value):
    try:
        n=float(value)
        return n if math.isfinite(n) and n>=0 else None
    except (TypeError,ValueError): return None


def default_reader(argv, **kwargs):
    return run(argv, **kwargs)


class Scan:
    def __init__(self, profile, region, tenancy, compartments, prices, limit=100, days=14, max_calls=300, reader=default_reader):
        self.profile,self.region,self.tenancy,self.compartments=profile,region,tenancy,compartments
        self.prices,self.limit,self.days,self.max_calls,self.reader=prices,limit,days,max_calls,reader
        self.cost_tag=None; self.budget_amount=None; self.budget_currency=None
        self.flags=[]; self.findings=[]; self.calls=0; self.cache={}; self.now=datetime.now(timezone.utc)
        self.end=self.now.replace(hour=0,minute=0,second=0,microsecond=0)
        self.start=self.end-timedelta(days=days)

    def gap(self,value):
        if value not in self.flags: self.flags.append(value)

    def read(self, argv, region=None):
        key=(region or self.region,tuple(argv))
        if key in self.cache: return self.cache[key]
        label=' '.join(argv[:3])
        for attempt in range(3):
            if self.calls>=self.max_calls:
                self.gap('call budget exhausted'); return None
            self.calls+=1
            result=self.reader(argv,profile=self.profile,region=region or self.region,sanitize=False,retain_identifiers=True,attempts=1)
            if result['ok']: break
            if result.get('error',{}).get('code')=='LifecyclePolicyNotFound': return {'missing_policy':True}
            if result.get('error',{}).get('status')!=429 or attempt==2:
                self.gap('unreadable: '+label); return None
            time.sleep(2**attempt)
        if result.get('truncated') or result.get('page_saturated'):
            self.gap('bounded sample: '+label); return None
        data=result['data']
        for part in ('data','items'):
            if isinstance(data,dict) and part in data: data=data[part]
        self.cache[key]=data
        return data

    def listing(self,path,compartment,extra=()):
        data=self.read([*path.split(),'--compartment-id',compartment,*extra,'--limit',str(self.limit)])
        if data is None: return None
        if not isinstance(data,list): self.gap('unexpected collection: '+path); return None
        return data[:self.limit]

    def metric(self,c,rid,namespace,metric,stat='percentile(0.95)',days=None,dimension='resourceId'):
        days=days or self.days
        if not re.fullmatch(r'[a-zA-Z0-9._:-]+',str(rid)):
            self.gap('invalid metric identifier'); return None
        query=f'{metric}[1d]{{{dimension} = "{rid}"}}.{stat}'
        data=self.read(['monitoring','metric-data','summarize-metrics-data','--compartment-id',c,'--namespace',namespace,
                        '--query-text',query,'--start-time',(self.end-timedelta(days=days)).isoformat(),'--end-time',self.end.isoformat()])
        if not isinstance(data,list): return None
        points={}
        for series in data:
            dims=series.get('dimensions') or {}
            if dims.get(dimension) not in (None,rid): continue
            for p in series.get('aggregated-datapoints') or []:
                value=numeric(p.get('value'))
                try: stamp=utc(p['timestamp'])
                except (KeyError,ValueError,TypeError): continue
                if value is not None and self.end-timedelta(days=days)<=stamp<self.end:
                    day=stamp.date().isoformat(); points[day]=max(points.get(day,0),value)
        if len(points)<math.ceil(days*.9):
            self.gap('insufficient metric coverage: '+metric+' '+ref(rid)); return None
        # Conservative maximum of daily P95s, never mislabelled as whole-window P95.
        return list(points.values())

    def price(self,part,q):
        if self.prices is None: return None
        try: return float(self.prices.cost(part,q))
        except (KeyError,StopIteration,ValueError): self.gap('price unavailable: '+part); return None

    def volume_cost(self,v):
        size,vpu=numeric(v.get('size-in-gbs')),numeric(v.get('vpus-per-gb'))
        if size is None or vpu is None: return None
        a,b=self.price('B91961',size),self.price('B91962',size*vpu)
        return None if a is None or b is None else a+b

    def add(self,pattern,row,evidence,estimate=None,confidence='review',action='Review with resource owner',hygiene=False):
        rid=row.get('id') or row.get('identifier') or row.get('name') or pattern
        # Do not emit account-controlled display names; stable hashes allow evidence joins.
        free=row.get('is-free-tier')
        confirmed=0.0 if free is True or hygiene else None
        recipe=RECIPES.get(pattern)
        if pattern=='D4' and str(rid).startswith('ocid1.bootvolume.'):
            recipe=('oci bv boot-volume update --boot-volume-id "${REVIEWED_BOOT_VOLUME_ID}" --vpus-per-gb 10',RECIPES['D4'][1])
        self.findings.append(dict(pattern=pattern,resource=ref(rid),evidence=clean(evidence)[0],
             monthly_estimate={'currency':'USD','list_price_exposure':round(estimate,4) if estimate is not None else None,
               'confirmed_savings':confirmed,'free_tier':'yes' if free is True else 'unknown/shared allowance needs billing evidence',
               'basis':'list price, pre-discount; exposure is not promised savings',
               'snapshot':self.prices.snapshot if self.prices else None},confidence=confidence,
             action={'kind':'MUTATING proposal only' if not hygiene else 'review only','proposal':action,'executed':False,
                     'command_template':recipe[0] if recipe else None,'verification':'shape-only; never executed',
                     'rollback':recipe[1] if recipe else 'Owner must supply the resource-specific change and rollback before execution',
                     'scope':'Resolve hashed resource privately; set explicit OCI profile/region and replace reviewed placeholders'}))

    def assess_compartment(self,c):
        limit=self.limit
        search=self.read(['search','resource','structured-search','--query-text',"query all resources where compartmentId = '"+c+"'",'--limit',str(limit)])
        # Search is cross-check only: service lists are authoritative for fields and joins.
        inst=self.listing('compute instance list',c)
        vols=self.listing('bv volume list',c)
        boots=self.listing('bv boot-volume list',c)
        attach=self.listing('compute volume-attachment list',c)
        ads=self.read(['iam','availability-domain','list','--compartment-id',self.tenancy])
        ba=[] if isinstance(ads,list) else None
        if ba is not None:
            for ad in ads:
                page=self.listing('compute boot-volume-attachment list',c,('--availability-domain',ad['name']))
                if page is None: ba=None; break
                ba.extend(page)
        active=lambda a: a.get('lifecycle-state') not in {'DETACHED','TERMINATED'}
        va=defaultdict(list);bva=defaultdict(list)
        for row in attach or []:
            if active(row):va[row.get('volume-id')].append(row)
        for row in ba or []:
            if active(row):bva[row.get('boot-volume-id')].append(row)
        instances={i['id']:i for i in inst or []}
        for collection,attachments,known,pattern in [(vols,va,attach,'D1'),(boots,bva,ba,'D2')]:
            for v in collection or []:
                if v.get('lifecycle-state')!='AVAILABLE': continue
                if known is not None and v['id'] not in attachments:
                    self.add(pattern,v,'No active attachment in fully read scoped attachment lists; duration unproven',self.volume_cost(v),'state-confirmed','Review retention and backup policy before deleting a volume')
                joined=attachments.get(v['id'],[])
                a=joined[0] if len(joined)==1 else None
                if joined and all(instances.get(row.get('instance-id'),{}).get('lifecycle-state')=='STOPPED' for row in joined):
                    self.add('D3',v,'Storage attached to a currently stopped instance; stop duration unknown, compute excluded',self.volume_cost(v),'state-confirmed','Confirm retirement and backup before removing retained storage')
                vpu=numeric(v.get('vpus-per-gb'))
                if vpu is not None and vpu>10:
                    # Compute-agent IOPS are per second; volume operation counts are not.
                    # All attached disks contribute, so this is a conservative upper proxy.
                    iid=a.get('instance-id') if a else None
                    metrics=[self.metric(c,iid,'oci_computeagent',m) if iid else None for m in ('DiskIopsRead','DiskIopsWritten')]
                    metrics.append(self.metric(c,v['id'],'oci_blockstore','VolumeGuaranteedIOPS','min()'))
                    if all(x is not None for x in metrics) and min(metrics[2])>0 and max(metrics[0])+max(metrics[1])<.25*min(metrics[2]):
                        savings=self.price('B91962',float(v['size-in-gbs'])*(vpu-10))
                        self.add('D4',v,'Instance-wide daily P95 IOPS below 25% of volume guaranteed IOPS; disk attribution and latency need review',savings,action='Review latency and IOPS; propose VPU 10 with original VPU as rollback')
        for i in inst or []:
            if i.get('lifecycle-state')!='RUNNING': continue
            stats=[self.metric(c,i['id'],'oci_computeagent',m) for m in ('CpuUtilization','MemoryUtilization','NetworksBytesIn','DiskBytesRead')]
            if any(s is None for s in stats):
                self.add('D5-guard',i,'Monitoring coverage insufficient; cannot classify idle',hygiene=True); continue
            if max(stats[0])<5 and max(stats[1])<10 and max(stats[2])<1e6 and max(stats[3])<1e6:
                shape=SHAPES.get(i.get('shape')); cfg=i.get('shape-config') or {}; cost=None
                if shape and numeric(cfg.get('ocpus')) is not None and numeric(cfg.get('memory-in-gbs')) is not None:
                    cpu=self.price(shape[0],cfg['ocpus']*730); mem=self.price(shape[1],cfg['memory-in-gbs']*730)
                    cost=cpu+mem if cpu is not None and mem is not None else None
                self.add('D5',i,'Daily P95 CPU <5%, memory <10%, network input and disk reads <1MB; 90% days covered',cost,action='Review batch/DR/licensing before resize; reboot required')
        self.load_balancers(c)
        self.databases(c)
        self.buckets(c)
        for n in self.listing('network nat-gateway list',c) or []:
            m=self.metric(c,n['id'],'oci_nat_gateway','BytesToNATgw','sum()')
            if m is not None and sum(m)==0: self.add('D12',n,'No observed NAT traffic; no gateway saving claimed',hygiene=True)
        for cluster in self.listing('ce cluster list',c) or []:
            for pool in self.listing('ce node-pool list',c,('--cluster-id',cluster['id'])) or []:
                detail=self.read(['ce','node-pool','get','--node-pool-id',pool['id']])
                nodes=(detail or {}).get('nodes',[])
                metrics=[self.metric(c,n['id'],'oci_computeagent','CpuUtilization') for n in nodes if n.get('lifecycle-state')=='ACTIVE']
                if metrics and all(m is not None and max(m)<10 for m in metrics):
                    self.add('D13',pool,'Worker CPU low; pod requests, memory, anti-affinity and capacity requirements unassessed',action='Inspect Kubernetes requests/limits before changing node pool')
        for path in ('bv backup list','bv boot-volume-backup list'):
            for b in self.listing(path,c) or []:
                if b.get('source-type')=='MANUAL' and not b.get('expiration-time'):
                    size=numeric(b.get('unique-size-in-gbs'))
                    self.add('D14',b,'Manual backup without expiration; retention and actual billed backup SKU/bytes need review',action='Review retention and source backup policy; deletion is irreversible')
        for ip in self.listing('network public-ip list',c,('--scope','REGION','--lifetime','RESERVED')) or []:
            if ip.get('lifecycle-state')=='AVAILABLE' and not ip.get('assigned-entity-id'):
                self.add('W12',ip,'Reserved IP unassigned; no IPv4 saving claimed',hygiene=True)
        for r in self.listing('compute capacity-reservation list',c) or []:
            reserved,used=numeric(r.get('reserved-instance-count')),numeric(r.get('used-instance-count'))
            if reserved is not None and used is not None and reserved>used:
                self.add('W13',r,'Unused reserved capacity; shape, duration and reservation billing need review')
        for vcn in self.listing('network vcn list',c) or []:
            subnets=self.listing('network subnet list',c,('--vcn-id',vcn['id']))
            if subnets==[]: self.add('W18',vcn,'VCN has no subnets in complete bounded listing; other dependencies unassessed',hygiene=True)

    def load_balancers(self,c):
        for path,namespace,traffic,dimension in [('lb load-balancer list','oci_lbaas','bytesReceived','resourceId'),('nlb network-load-balancer list','oci_nlb','ProcessedBytes','RESOURCEID')]:
            for lb in self.listing(path,c) or []:
                m=self.metric(c,lb['id'],namespace,traffic,'sum()',dimension=dimension)
                con=self.metric(c,lb['id'],namespace,'activeConnections' if namespace=='oci_lbaas' else 'NewConnections','max()',dimension=dimension)
                if m is not None and con is not None and sum(m)==0 and max(con)==0:
                    self.add('D6',lb,'No traffic or connections across covered days; standby schedule needs review',hygiene=namespace=='oci_nlb')
                if namespace=='oci_lbaas':
                    total=self.metric(c,lb['id'],namespace,'backendServers','max()')
                    bad=self.metric(c,lb['id'],namespace,'unhealthyBackendServers','max()')
                    if total is not None and bad is not None and max(total)>0 and min(bad)>=max(total):
                        self.add('D7',lb,'Unhealthy backend daily peaks match observed counts; align backend sets and timestamps before diagnosing outage',action='Investigate backend health before considering retirement')

    def databases(self,c):
        for db in self.listing('db autonomous-database list',c) or []:
            if db.get('lifecycle-state')=='STOPPED':
                self.add('D8',db,'ADB stopped; compute excluded; storage and free-tier eligibility require billing check'); continue
            cpu=self.metric(c,db['id'],'oci_autonomous_database','CpuUtilization')
            sessions=self.metric(c,db['id'],'oci_autonomous_database','Sessions','max()')
            if cpu is not None and sessions is not None and max(cpu)<10 and max(sessions)<=1:
                self.add('D8',db,'Daily CPU P95 <10%, sessions <=1; confirm month-end/DR role and autoscaling')
            used=self.metric(c,db['id'],'oci_autonomous_database','StorageUsed','max()')
            alloc=self.metric(c,db['id'],'oci_autonomous_database','StorageAllocated','max()')
            if used is not None and alloc is not None and max(alloc)>0 and max(used)<.2*max(alloc):
                self.add('D9',db,'Used storage below 20% allocation; units, SKU and service minimum require review')

    def buckets(self,c):
        ns=self.read(['os','ns','get'])
        if not isinstance(ns,str): return
        for b in self.listing('os bucket list',c,('--namespace-name',ns)) or []:
            name=b.get('name')
            if not isinstance(name,str): continue
            details=self.read(['os','bucket','get','--namespace-name',ns,'--bucket-name',name,'--fields','approximateSize'])
            policy=self.read(['os','object-lifecycle-policy','get','--namespace-name',ns,'--bucket-name',name])
            size=numeric((details or {}).get('approximate-size'))
            if policy=={'missing_policy':True}:
                self.add('D10',b,'No lifecycle policy; storage access and minimum retention need review'+(f'; bytes={size:g}' if size is not None else ''),hygiene=size is not None and size<=10*1024**3)
            m=self.metric(c,name,'oci_objectstorage','AllRequests','sum()',days=30,dimension='bucketName')
            if m is not None and sum(m)==0: self.add('D11',b,'No requests in 30 covered days; evaluate retrieval charges before storage tier change')
            for part in self.read(['os','multipart','list','--namespace-name',ns,'--bucket-name',name,'--limit',str(self.limit)]) or []:
                try: old=(self.now-utc(part['time-created'])).days>=7
                except (KeyError,TypeError,ValueError): old=False
                if old: self.add('W11-parts',b,'Uncommitted multipart upload older than seven days; size unavailable')

    def governance(self):
        subscriptions=self.read(['iam','region-subscription','list','--tenancy-id',self.tenancy])
        home=next((x.get('region-name') for x in subscriptions or [] if x.get('is-home-region')),None)
        self.gap('regional scope only: other regions require separate explicit scans')
        budgets=self.listing('budgets budget budget list',self.tenancy)
        if budgets==[]: self.add('W15',{'id':self.tenancy},'No budget in a complete bounded tenancy list',hygiene=True)
        if home:
            recs=self.read(['optimizer','recommendation-summary','list','--compartment-id',self.tenancy,'--compartment-id-in-subtree','true','--limit',str(self.limit)],region=home)
            for rec in recs or []:
                actions=self.read(['optimizer','resource-action-summary','list','--compartment-id',self.tenancy,'--compartment-id-in-subtree','true','--recommendation-id',rec['id'],'--limit',str(self.limit)],region=home)
                for action in actions or []:
                    if action.get('status')=='PENDING':
                        self.add('D18',{'id':action.get('resource-id')},'Cloud Advisor pending: '+str(rec.get('name')),hygiene=True)
        else: self.gap('Cloud Advisor home region unresolved')
        end=self.end-timedelta(days=2); start=end-timedelta(days=30)
        # Explicit region/compartment filter prevents accidental account-wide billing disclosure.
        filt={'operator':'AND','dimensions':[{'key':'region','value':self.region}], 'filters':[{'operator':'OR','dimensions':[{'key':'compartmentId','value':c} for c in self.compartments]}]}
        data=self.read(['usage-api','usage-summary','request-summarized-usages','--tenant-id',self.tenancy,'--time-usage-started',start.isoformat(),'--time-usage-ended',end.isoformat(),'--granularity','DAILY','--query-type','COST','--group-by','["service","skuPartNumber"]','--filter',json.dumps(filt),'--limit',str(self.limit)])
        if data is not None:
            try: rows=cost_rows(data,start,end)
            except ValueError: self.gap('invalid cost response window or currency'); rows=[]
            daily=defaultdict(lambda:defaultdict(float))
            for row in rows:
                if not row.get('is-forecast'): daily[(row.get('service'),row['currency'])][row['time-usage-started']]+=float(row['computed-amount'])
            for (service,currency),points in daily.items():
                values=[v for _,v in sorted(points.items())]
                if len(values)>=8:
                    baseline=values[:-1]; mean=sum(baseline)/len(baseline); sigma=(sum((x-mean)**2 for x in baseline)/len(baseline))**.5
                    if values[-1]>mean+3*sigma:
                        self.add('D15',{'id':service},f'Settled nonzero daily cost anomaly in {currency}; last value {values[-1]:.2f}; no FX or USD conversion',hygiene=True)
        if self.budget_amount is not None and self.budget_currency:
            stop=self.end.replace(day=1)
            next_month=(stop.replace(day=28)+timedelta(days=4)).replace(day=1)
            history=(stop-timedelta(days=62)).replace(day=1)
            forecast=self.read(['usage-api','usage-summary','request-summarized-usages','--tenant-id',self.tenancy,
                '--time-usage-started',history.isoformat(),'--time-usage-ended',stop.isoformat(),
                '--granularity','MONTHLY','--query-type','COST','--group-by','["service"]',
                '--forecast',json.dumps({'forecastType':'BASIC','timeForecastStarted':stop.isoformat(),'timeForecastEnded':next_month.isoformat()}),
                '--filter',json.dumps(filt),'--limit',str(self.limit)])
            predicted=[r for r in forecast or [] if r.get('is-forecast') and r.get('currency')==self.budget_currency and r.get('time-usage-started') and utc(r['time-usage-started'])==stop]
            if predicted and sum(float(r.get('computed-amount') or 0) for r in predicted)>self.budget_amount:
                self.add('D16',{'id':'scoped-budget'},'Month-end forecast exceeds explicit scoped budget in '+self.budget_currency,hygiene=True)
        else: self.gap('D16 forecast needs explicit scoped budget amount and currency')
        if self.cost_tag:
            namespace,key=self.cost_tag.split('.',1)
            tagged=self.read(['usage-api','usage-summary','request-summarized-usages','--tenant-id',self.tenancy,
                '--time-usage-started',start.isoformat(),'--time-usage-ended',end.isoformat(),'--granularity','DAILY','--query-type','COST',
                '--group-by-tag',json.dumps([{'namespace':namespace,'key':key}]),'--filter',json.dumps(filt),'--limit',str(self.limit)])
            totals=defaultdict(float); missing=defaultdict(float)
            for row in tagged or []:
                amount=numeric(row.get('computed-amount')); currency=row.get('currency')
                if amount is None or not currency or currency.strip() in {'','NA'}: continue
                totals[currency]+=amount
                tags=row.get('tags') or []
                if not any(t.get('namespace')==namespace and t.get('key')==key and t.get('value') for t in tags): missing[currency]+=amount
            for currency,total in totals.items():
                if total>0 and missing[currency]/total>.2:
                    self.add('D17',{'id':'cost-tag'},'More than 20% of positive scoped spend untagged in '+currency,hygiene=True)
        else: self.gap('D17 untagged spend needs --cost-tag namespace.key')

    def report(self):
        for c in self.compartments:
            if not re.fullmatch(r'ocid1\.[a-z0-9._-]+',c): raise ValueError('Invalid compartment identifier')
            self.assess_compartment(c)
        self.governance()
        return dict(schema='oci-waste.v1',region=self.region,compartments=[ref(c) for c in self.compartments],
                    window={'start':self.start.isoformat(),'end':self.end.isoformat()},calls=self.calls,
                    findings=self.findings,coverage_gaps=self.flags,complete=False,
                    totals={'confirmed_savings':None,'reason':'shared free allowances, overlapping findings and billing eligibility unproven'})


def markdown(report):
    lines=['# OCI waste assessment','',f"Region: {report['region']}. Read calls: {report['calls']}. Bounded sample; absence is not proven.",
           'List-price exposure is not confirmed savings. Shared allowances and overlapping findings are not summed.','',
           '| Pattern | Resource | Evidence | USD monthly exposure |','|---|---|---|---:|']
    for f in report['findings']:
        amount=f['monthly_estimate']['list_price_exposure']
        lines.append(f"| {f['pattern']} | {f['resource']} | {f['evidence'].replace('|','/')} | {amount if amount is not None else 'unknown'} |")
    lines+=['','## Coverage gaps','']+['- '+str(f) for f in report['coverage_gaps']]
    lines+=['','## Review proposals (never executed)','']
    for f in report['findings']:
        action=f['action'];lines.append('- '+f['resource']+': '+action['proposal'])
        if action.get('command_template'):
            lines.extend(['', '```bash', '# MUTATING [shape-verified] — template; resolve identity and scope privately',
                          '# rollback: '+action['rollback'], action['command_template'], '```', ''])
    return '\n'.join(lines)+'\n'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--compartment',action='append',required=True)
    p.add_argument('--tenancy',default=os.environ.get('TENANCY_ID'))
    p.add_argument('--profile',default=os.environ.get('PROFILE'))
    p.add_argument('--region',default=os.environ.get('REGION'))
    p.add_argument('--max-resources',type=int,default=100)
    p.add_argument('--max-calls',type=int,default=300)
    p.add_argument('--days',type=int,default=14)
    p.add_argument('--price-cache',type=Path)
    p.add_argument('--cost-tag',help='Explicit cost-tracking namespace.key')
    p.add_argument('--budget-amount',type=float)
    p.add_argument('--budget-currency')
    p.add_argument('--format',choices=['json','md'],default='md')
    a=p.parse_args()
    if not all((a.tenancy,a.profile,a.region)) or not 1<=a.max_resources<=200 or not 7<=a.days<=30 or not 1<=a.max_calls<=500:
        p.error('Explicit tenancy/profile/region required; resources 1..200, days 7..30, calls 1..500')
    try: prices=load_prices(a.price_cache)
    except Exception: prices=None
    scan=Scan(a.profile,a.region,a.tenancy,a.compartment,prices,a.max_resources,a.days,a.max_calls)
    if a.cost_tag and not re.fullmatch(r'[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',a.cost_tag): p.error('Invalid cost tag')
    if (a.budget_amount is None)!=(a.budget_currency is None) or (a.budget_amount is not None and (numeric(a.budget_amount) is None or not re.fullmatch('[A-Z]{3}',a.budget_currency))): p.error('Budget requires a finite nonnegative amount and three-letter uppercase currency')
    scan.cost_tag=a.cost_tag; scan.budget_amount=a.budget_amount; scan.budget_currency=a.budget_currency
    if prices is None: scan.gap('public price API unavailable')
    try: report=scan.report()
    except Exception: p.exit(1,'Assessment stopped on invalid service data; no resources changed.\n')
    print(emit(report) if a.format=='json' else markdown(report))


if __name__=='__main__': main()
