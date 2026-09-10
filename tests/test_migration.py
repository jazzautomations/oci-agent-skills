import importlib.util
import json
from pathlib import Path
import pytest
R=Path(__file__).resolve().parents[1]

def module(name,skill,file):
    spec=importlib.util.spec_from_file_location(name,R/'skills'/skill/'scripts'/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
n=module('normal','oci-migration-assess','inventory_normalize.py');m=module('mapprice','oci-migration-map','map_and_price.py');lz=module('landing','oci-migration-landing-zone','emit_tfvars.py')


def test_fixture_preserves_unknowns_and_redacts():
    raw=json.loads((R/'skills/oci-migration-assess/fixtures/aws-sample.json').read_text());out=n.normalize(raw)
    assert out['synthetic'] and out['compute'][0]['observed']['mem_p95'] is None
    assert out['scope']['services_not_readable']
    assert raw['compute'][0]['id'] not in json.dumps(out)
    assert n.normalize(out)['compute']==out['compute']


def test_source_missing_is_not_empty_inventory():
    with pytest.raises(ValueError):n.normalize({'source_cloud':'aws'})
    raw={'source_cloud':'azure','scope':{'regions_scanned':['eastus'],'services_not_readable':[]}}
    assert 'compute not exported' in n.normalize(raw)['scope']['services_not_readable']


@pytest.mark.parametrize('cloud,data',[('gcp',{'instances':[{'id':'1','machineType':'n2-standard-4'}]}),('azure',{'vms':[{'id':'2','hardwareProfile':{'vmSize':'Standard_D4s_v5'}}]})])
def test_missing_size_never_guessed(cloud,data):
    out=n.normalize(dict(source_cloud=cloud,scope={'regions_scanned':['region'],'services_not_readable':[]},**data))
    assert out['compute'][0]['vcpu'] is None and out['compute'][0]['memory_gb'] is None


def test_x86_arm_and_memory_limits():
    assert m.cpu_shape({'arch':'arm64','vcpu':8,'memory_gb':32})['ocpus']==4
    assert m.cpu_shape({'arch':'x86_64','vcpu':2,'cores':1,'memory_gb':128})['ocpus']==2
    with pytest.raises(ValueError):m.cpu_shape({'arch':'x86_64','vcpu':64,'memory_gb':1600})
    with pytest.raises(ValueError):m.cpu_shape({'vcpu':4,'memory_gb':16})


def test_volume_solver_rejects_impossible_and_unknown():
    assert m.volume_target({'size_gb':8,'iops':100,'throughput_mbps':1})['size_gb']==50
    assert m.volume_target({'size_gb':1000,'iops':16000,'throughput_mbps':500})['vpu']>=20
    with pytest.raises(ValueError):m.volume_target({'size_gb':1,'iops':9000000,'throughput_mbps':10000})
    with pytest.raises(ValueError):m.volume_target({'size_gb':100,'iops':None,'throughput_mbps':None})


def test_landing_zone_rejects_overlap_and_emits_typed_draft():
    inv={'network':[{'cidrs':['10.20.0.0/16']}],'database':[{}]}
    with pytest.raises(ValueError):lz.plan(inv,'us-ashburn-1','migdemo','10.20.0.0/16')
    out=lz.plan(inv,'us-ashburn-1','migdemo','10.80.0.0/16')
    assert out['tfvars']['define_net'] is True
    assert out['tfvars']['tt_vcn1_web_subnet_is_private'] is True
    assert len(out['tfvars'])<250


def test_no_false_full_savings():
    class Book:
        snapshot='test'
        def cost(self,part,q):return 1
    inv=n.normalize(json.loads((R/'skills/oci-migration-assess/fixtures/aws-sample.json').read_text()))
    out=m.assess(inv,Book())
    assert out['totals']['full_savings'] is None
    assert out['totals']['priced_resources']<out['totals']['total_resources']
    assert len(out['questions'])==10
