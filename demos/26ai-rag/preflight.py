#!/usr/bin/env python3
"""Read-only prerequisites; prints selected capability fields without account identifiers."""
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from lib.oci_ro import run


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--offline',action='store_true');a=p.parse_args()
    report={'database_sql':'not executed','tools':{},'capabilities':{},'gaps':[]}
    for tool,args in [('oci',['--version']),('java',['-version']),('sql',['-V'])]:
        if shutil.which(tool):
            result=subprocess.run([tool,*args],capture_output=True,text=True,timeout=20)
            report['tools'][tool]=(result.stdout+result.stderr).strip()[:200]
        else:report['tools'][tool]='missing';report['gaps'].append(tool+' missing')
    try:report['tools']['oracledb']=importlib.metadata.version('oracledb')
    except importlib.metadata.PackageNotFoundError:report['tools']['oracledb']='missing';report['gaps'].append('python-oracledb missing from this interpreter')
    if not a.offline:
        profile,region,c=(os.environ.get(k) for k in ('PROFILE','REGION','COMPARTMENT_ID'))
        if not all((profile,region,c)):p.error('Set explicit PROFILE REGION COMPARTMENT_ID')
        queries=[('versions',['db','autonomous-db-version','list','--compartment-id',c,'--limit','50','--query','data[].{version:version,workload:"db-workload",free:"is-free-tier-enabled",paid:"is-paid-enabled"}']),
          ('genai_models',['generative-ai','model-collection','list-models','--compartment-id',c,'--limit','50','--query','data.items[].{name:"display-name",state:"lifecycle-state",retired:"time-on-demand-retired"}']),
          ('genai_limits',['limits','value','list','--compartment-id',c,'--service-name','ai-generative','--limit','100','--query','data[].{name:name,value:value}'])]
        for name,argv in queries:
            result=run(argv,profile=profile,region=region)
            if result['ok']:
                report['capabilities'][name]=result['data']['items']
                if result.get('truncated'):report['gaps'].append(name+' bounded sample')
            else:report['gaps'].append(name+' unreadable')
    report['gaps']+=['Provisioning eligibility is not proved by version listing','No SQL/index/model inference has been run','Select AI requires usable quota and separate explicit setup']
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
