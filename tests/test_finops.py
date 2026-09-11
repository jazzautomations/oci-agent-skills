import importlib.util
import sys
from pathlib import Path
from datetime import timedelta
from types import SimpleNamespace
import json
from unittest.mock import Mock
import pytest
R=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('waste',R/'skills/oci-finops-waste/scripts/waste_scan.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
from lib import oci_ro


def scan(reader=None):return w.Scan('test','us-chicago-1','ocid1.tenancy.oc1..example',['ocid1.compartment.oc1..example'],None,reader=reader or Mock())


def test_no_metrics_is_not_idle():
    s=scan(lambda *a,**k:dict(ok=True,data={'data':[]},truncated=False))
    assert s.metric('c','ocid1.instance.oc1..example','oci_computeagent','CpuUtilization') is None
    assert any('coverage' in g for g in s.flags)


def test_metric_needs_distinct_days_and_ignores_outside_window():
    s=scan();data=[{'aggregated-datapoints':[{'timestamp':s.start.isoformat(),'value':0}]*20}]
    s.reader=lambda *a,**k:dict(ok=True,data={'data':data},truncated=False)
    assert s.metric('c','resource','ns','Metric') is None
    data[0]['aggregated-datapoints']=[{'timestamp':(s.start+timedelta(days=i)).isoformat(),'value':i} for i in range(14)]
    s.cache.clear();assert len(s.metric('c','resource','ns','Metric'))==14


def test_saturated_attachment_page_cannot_prove_orphan():
    s=scan(lambda *a,**k:dict(ok=True,data={'data':[]},truncated=True))
    assert s.listing('compute volume-attachment list','c') is None
    assert 'bounded sample' in s.flags[0]


def test_bounded_backoff_and_call_budget(monkeypatch):
    sleeps=[];monkeypatch.setattr(w.time,'sleep',sleeps.append)
    s=scan(lambda *a,**k:dict(ok=False,error={'status':429}));s.max_calls=2
    assert s.read(['compute','instance','list']) is None
    assert s.calls==2 and sleeps==[1,2]
    assert 'call budget exhausted' in s.flags


def test_free_tier_and_names_never_turn_into_savings():
    s=scan();s.add('D8',{'id':'account-secret','display-name':'private-name','is-free-tier':True},'Stopped',100)
    f=s.findings[0]
    assert f['monthly_estimate']['confirmed_savings']==0
    assert 'account-secret' not in json.dumps(f) and 'private-name' not in json.dumps(f)


def test_wrapper_internal_join_opt_in(monkeypatch):
    rid='ocid1.instance.oc1..abcdefghijklmnop'
    monkeypatch.setattr(oci_ro,'run_process',lambda *a,**k:SimpleNamespace(returncode=0,stderr='',stdout=json.dumps({'data':[{'id':rid}]})))
    argv=['compute','instance','list','--compartment-id','ocid1.compartment.oc1..example','--limit','1']
    assert rid not in str(oci_ro.run(argv,sanitize=False)['data'])
    assert oci_ro.run(argv,sanitize=False,retain_identifiers=True)['data']['data'][0]['id']==rid
    assert not oci_ro.run(argv,retain_identifiers=True)['ok']


def test_missing_policy_is_specific_not_any_404():
    s=scan(lambda *a,**k:dict(ok=False,error={'status':404,'code':'LifecyclePolicyNotFound'}))
    assert s.read(['os','object-lifecycle-policy','get'])=={'missing_policy':True}
    s.reader=lambda *a,**k:dict(ok=False,error={'status':404,'code':'NotAuthorizedOrNotFound'})
    assert s.read(['os','object-lifecycle-policy','get']) is None


@pytest.mark.parametrize('kind,attachment,expected',[('block',[],['D1']),('boot',[],['D2']),('boot',[{'boot-volume-id':'v','instance-id':'i','lifecycle-state':'ATTACHING'}],['D3']),('block',[{'volume-id':'v','instance-id':'i','lifecycle-state':'ATTACHED'}],['D3'])])
def test_storage_joins(kind,attachment,expected):
    s=scan();s.load_balancers=s.databases=s.buckets=lambda c:None;s.metric=lambda *a,**k:None
    s.read=lambda argv,**k:[{'name':'ad1'}] if argv[:3]==['iam','availability-domain','list'] else []
    def listing(path,c,extra=()):
        return {'compute instance list':[{'id':'i','lifecycle-state':'STOPPED'}],
          'bv volume list':[{'id':'v','lifecycle-state':'AVAILABLE','vpus-per-gb':10}] if kind=='block' else [],
          'bv boot-volume list':[{'id':'v','lifecycle-state':'AVAILABLE','vpus-per-gb':10}] if kind=='boot' else [],
          'compute volume-attachment list':attachment if kind=='block' else [],
          'compute boot-volume-attachment list':attachment if kind=='boot' else []}.get(path,[])
    s.listing=listing;s.assess_compartment('ocid1.compartment.oc1..example')
    assert [f['pattern'] for f in s.findings]==expected


def test_database_stopped_idle_and_allocation():
    s=scan();s.listing=lambda *a,**k:[{'id':'free','lifecycle-state':'STOPPED','is-free-tier':True},{'id':'paid','lifecycle-state':'AVAILABLE'}]
    s.metric=lambda c,r,ns,m,*a,**k:[{'CpuUtilization':1,'Sessions':1,'StorageUsed':10,'StorageAllocated':100}[m]]*14
    s.databases('c')
    assert [f['pattern'] for f in s.findings]==['D8','D8','D9']
    assert s.findings[0]['monthly_estimate']['confirmed_savings']==0


def test_lb_names_nlb_dimension_and_empty_backends():
    s=scan();seen=[]
    s.listing=lambda path,c:[{'id':path}]
    def metric(c,r,ns,name,*args,**kwargs):
        seen.append((ns,name,kwargs.get('dimension')))
        return [0]*14
    s.metric=metric;s.load_balancers('c')
    assert [f['pattern'] for f in s.findings]==['D6','D6']
    assert ('oci_lbaas','bytesReceived','resourceId') in seen
    assert ('oci_nlb','ProcessedBytes','RESOURCEID') in seen
    s.findings.clear()
    s.metric=lambda c,r,ns,m,*a,**k:[2 if 'BackendServers' in m or m=='backendServers' else 0]*14
    s.load_balancers('c');assert 'D7' in [f['pattern'] for f in s.findings]


def test_bucket_lifecycle_cold_and_abandoned_upload():
    s=scan();s.listing=lambda *a,**k:[{'name':'private-bucket'}];s.metric=lambda *a,**k:[0]*30
    def read(argv):
        if argv[1:3]==['ns','get']:return 'private-namespace'
        if argv[1:3]==['bucket','get']:return {'approximate-size':100}
        if argv[1:3]==['object-lifecycle-policy','get']:return {'missing_policy':True}
        if argv[1:3]==['multipart','list']:return [{'time-created':(s.now-timedelta(days=8)).isoformat()}]
    s.read=read;s.buckets('c')
    assert [f['pattern'] for f in s.findings]==['D10','D11','W11-parts']
    assert 'private-bucket' not in json.dumps(s.findings)


def test_remaining_inventory_patterns():
    s=scan();s.load_balancers=s.databases=s.buckets=lambda c:None
    def listing(path,c,extra=()):
        return {
         'compute instance list':[{'id':'i','lifecycle-state':'RUNNING'}],
         'bv volume list':[{'id':'v','lifecycle-state':'AVAILABLE','vpus-per-gb':20,'size-in-gbs':100}],
         'compute volume-attachment list':[{'volume-id':'v','instance-id':'i','lifecycle-state':'ATTACHED'}],
         'network nat-gateway list':[{'id':'nat'}], 'ce cluster list':[{'id':'cluster'}],
         'ce node-pool list':[{'id':'pool'}],
         'bv backup list':[{'id':'backup','source-type':'MANUAL','expiration-time':None}],
         'network public-ip list':[{'id':'ip','lifecycle-state':'AVAILABLE'}],
         'compute capacity-reservation list':[{'id':'reservation','reserved-instance-count':2,'used-instance-count':0}],
         'network vcn list':[{'id':'vcn'}]}.get(path,[])
    s.listing=listing
    s.read=lambda argv,**k: {'nodes':[{'id':'worker','lifecycle-state':'ACTIVE'}]} if argv[:3]==['ce','node-pool','get'] else []
    s.metric=lambda c,r,ns,m,*a,**k:[1000 if m=='VolumeGuaranteedIOPS' else 0]*14
    s.assess_compartment('c')
    assert {'D4','D5','D12','D13','D14','W12','W13','W18'} <= {f['pattern'] for f in s.findings}
    assert next(f for f in s.findings if f['pattern']=='D14')['monthly_estimate']['list_price_exposure'] is None


def test_governance_anomaly_forecast_tags_and_advisor():
    s=scan();s.budget_amount=10;s.budget_currency='BRL';s.cost_tag='Finance.Owner'
    s.listing=lambda *a,**k:[]
    regions=[]
    def read(argv,region=None):
        if argv[:3]==['iam','region-subscription','list']:return [{'region-name':'home-region','is-home-region':True}]
        if argv[0]=='optimizer':
            regions.append(region)
            return [{'id':'rec','name':'Advisor'}] if argv[1]=='recommendation-summary' else [{'status':'PENDING','resource-id':'private-id','url':'private-url'}]
        if '--forecast' in argv:return [{'is-forecast':True,'currency':'BRL','time-usage-started':s.end.replace(day=1).isoformat(),'computed-amount':100}]
        if '--group-by-tag' in argv:return [{'currency':'BRL','computed-amount':100,'tags':[]}]
        if argv[0]=='usage-api':
            start=s.end-timedelta(days=32)
            return [{'service':'Compute','currency':'BRL','computed-amount':100 if day==29 else 1,
                     'time-usage-started':(start+timedelta(days=day)).isoformat(),
                     'time-usage-ended':(start+timedelta(days=day+1)).isoformat()} for day in range(30)]
    s.read=read;s.governance()
    assert {f['pattern'] for f in s.findings}=={'W15','D18','D15','D16','D17'}
    assert regions==['home-region','home-region']
    assert 'private-url' not in json.dumps(s.findings)
    assert all(f['action']['executed'] is False for f in s.findings)
    assert s.flags == []


def governance_reader(s, *, days=8, forecast=True, amount=10):
    def read(argv, **kwargs):
        if argv[:3]==['iam','region-subscription','list']:
            return [{'region-name':s.region,'is-home-region':True}]
        if argv[0]=='optimizer': return []
        if '--forecast' in argv:
            return ([{'is-forecast':True,'currency':'USD','computed-amount':amount,
                      'time-usage-started':s.end.replace(day=1).isoformat()}] if forecast else [])
        if '--group-by-tag' in argv:
            return [{'currency':'USD','computed-amount':amount,'tags':[{'namespace':'Finance','key':'Owner','value':'team'}]}]
        start=s.end-timedelta(days=32)
        return [{'service':'Compute','currency':'USD','computed-amount':1,
                 'time-usage-started':(start+timedelta(days=i)).isoformat(),
                 'time-usage-ended':(start+timedelta(days=i+1)).isoformat()} for i in range(days)]
    return read


def governance_scan(**options):
    s=scan();s.cost_tag='Finance.Owner';s.budget_amount=20;s.budget_currency='USD'
    s.listing=lambda *a,**k:[]
    s.assess_compartment=lambda c:None
    s.reader=None
    s.read=governance_reader(s,**options)
    return s


def test_regional_scope_boundary_is_not_an_unavoidable_coverage_failure():
    s=governance_scan()
    report=s.report()
    assert report['coverage_gaps']==[]
    assert report['scope_limitations'] and report['complete'] is False
    assert report['totals']['confirmed_savings'] is None
    assert 'Only the supplied region' in w.markdown(report)
    sys.path.insert(0,str(R/'scripts'))
    from check_skill_scripts import outcome
    assert outcome(0,json.dumps(report),'')=='passed'
    report['coverage_gaps'].append('unreadable: compute instance list')
    assert outcome(0,json.dumps(report),'')=='ran, gap'


@pytest.mark.parametrize('options,detector', [({'days':0},'D15'),({'days':7},'D15'),
                                           ({'forecast':False},'D16'),({'amount':0},'D17')])
def test_missing_finops_evidence_stays_a_coverage_gap(options,detector):
    report=governance_scan(**options).report()
    assert any(g.startswith(detector) for g in report['coverage_gaps'])
    assert all(f['pattern']!=detector for f in report['findings'])


def test_multiattached_volume_is_not_retired_with_one_stopped_vm():
    s=scan();s.load_balancers=s.databases=s.buckets=lambda c:None;s.metric=lambda *a,**k:None;s.read=lambda *a,**k:[]
    def listing(path,c,extra=()):
        return {'compute instance list':[{'id':'stopped','lifecycle-state':'STOPPED'},{'id':'running','lifecycle-state':'RUNNING'}],
         'bv volume list':[{'id':'v','lifecycle-state':'AVAILABLE','vpus-per-gb':10}],
         'compute volume-attachment list':[{'volume-id':'v','instance-id':iid,'lifecycle-state':'ATTACHED'} for iid in ['running','stopped']]}.get(path,[])
    s.listing=listing;s.assess_compartment('c')
    assert not {'D1','D3'} & {f['pattern'] for f in s.findings}
