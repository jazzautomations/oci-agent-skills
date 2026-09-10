#!/usr/bin/env python3
"""Dedicated demo lifecycle. Dry-run by default; never touches an existing unrelated DB."""
import argparse
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import uuid


def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
    os.fchmod(fd,0o600)
    with os.fdopen(fd,'w') as f:json.dump(data,f,indent=2)


def create_payload(mode,compartment,name,acl):
    address=ipaddress.ip_network(acl,strict=True)
    if address.prefixlen==0:raise ValueError('An unrestricted ACL is not allowed for this demo')
    if not re.fullmatch('[A-Za-z][A-Za-z0-9]{0,29}',name):raise ValueError('Database name must be 1..30 alphanumerics')
    if not re.fullmatch(r'ocid1\.(tenancy|compartment)\.[a-z0-9._-]+',compartment):raise ValueError('Explicit compartment required')
    data=dict(compartmentId=compartment,dbName=name,displayName='26ai RAG demo',dbVersion='26ai',dbWorkload='OLTP',
        isMtlsConnectionRequired=False,whitelistedIps=[str(address)],isAutoScalingEnabled=False)
    if mode=='free':data['isFreeTier']=True
    elif mode=='developer':data['isDevTier']=True
    else:data.update(isFreeTier=False,computeModel='ECPU',computeCount=2,dataStorageSizeInGBs=20,licenseModel='LICENSE_INCLUDED')
    return data


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('operation',choices=['provision','teardown'])
    p.add_argument('--mode',choices=['free','developer','paid'],default='free');p.add_argument('--profile',default=os.environ.get('PROFILE'))
    p.add_argument('--region',default=os.environ.get('REGION'));p.add_argument('--compartment',default=os.environ.get('COMPARTMENT_ID'))
    p.add_argument('--name',default='RAGKIT26');p.add_argument('--acl',default=os.environ.get('RAG_ACL'))
    p.add_argument('--state',type=Path,default=Path('.local/rag26/state.json'));p.add_argument('--dry-run',action='store_true')
    p.add_argument('--execute',action='store_true');p.add_argument('--confirm')
    a=p.parse_args()
    if not a.profile or not a.region:p.error('Set explicit PROFILE and REGION')
    try:
        state=json.loads(a.state.read_text()) if a.state.exists() else None
        if a.operation=='provision':
            payload=create_payload(a.mode,a.compartment,a.name,a.acl)
            desired=hashlib.sha256(json.dumps([payload,a.profile,a.region],sort_keys=True).encode()).hexdigest()
            if state and state.get('request_hash')!=desired:raise ValueError('State belongs to a different scope or database request')
            if state and state.get('deleted'):raise ValueError('Use a fresh state path for a new demo; retained state proves prior teardown')
            if state and state.get('adb_id'):
                print('This request already has a recorded database. Run preflight/get; no create repeated.');return
            private=a.state.with_name('create.private.json')
            token=state.get('retry_token') if state else str(uuid.uuid4())
            argv=['oci','db','autonomous-database','create','--from-json','file://'+str(private.resolve()),'--opc-retry-token',token,
              '--wait-for-state','AVAILABLE','--max-wait-seconds','2400','--wait-interval-seconds','30','--profile',a.profile,'--region',a.region]
            confirmation='CREATE:'+a.name
            if not a.execute or a.dry_run:
                print('# MUTATING — not run; exact command after writing private create JSON from explicit inputs')
                print(shlex.join(argv));print('Mode:',a.mode,'; db-version: 26ai; paid = 2 ECPU; rollback: teardown using recorded state')
                return
            if a.confirm!=confirmation:raise ValueError('Execution requires --confirm '+confirmation)
            pw=os.environ.get('RAG_ADMIN_PASSWORD','')
            if not 12<=len(pw)<=30 or '"' in pw or 'admin' in pw.lower() or not all(re.search(r,pw) for r in ['[a-z]','[A-Z]','[0-9]']):raise ValueError('Set a valid RAG_ADMIN_PASSWORD privately')
            state=state or dict(request_hash=desired,retry_token=token,profile=a.profile,region=a.region,owned_demo=True)
            save(a.state,state);payload['adminPassword']=pw;save(private,payload)
            try:result=subprocess.run(argv,capture_output=True,text=True,timeout=2500)
            finally:private.unlink(missing_ok=True)
            if result.returncode:raise ValueError('Creation did not finish; keep state and retry token for recovery. Inspect privately; do not create under a new name.')
            data=json.loads(result.stdout)['data'];state['adb_id']=data['id'];save(a.state,state)
            print('Database recorded privately. Run preflight/version check before SQL setup.')
        else:
            if not state or not state.get('owned_demo') or not state.get('adb_id'):raise ValueError('Teardown requires this kit\'s recorded database; no arbitrary ID accepted')
            if (a.profile,a.region)!=(state['profile'],state['region']):raise ValueError('Teardown scope differs from creation')
            if state.get('deleted'):print('Recorded teardown already completed.');return
            rid=state['adb_id'];suffix=hashlib.sha256(rid.encode()).hexdigest()[:12]
            argv=['oci','db','autonomous-database','delete','--autonomous-database-id',rid,'--force','--wait-for-state','SUCCEEDED','--max-wait-seconds','1800','--profile',a.profile,'--region',a.region]
            if not a.execute or a.dry_run:
                shown=argv.copy();shown[shown.index(rid)]='<database from private state>'
                print('# MUTATING — not run; irreversible database deletion');print(shlex.join(shown));print('Required confirmation: DELETE:'+suffix);return
            if a.confirm!='DELETE:'+suffix:raise ValueError('Confirmation does not match recorded database')
            result=subprocess.run(argv,capture_output=True,text=True,timeout=1900)
            if result.returncode:raise ValueError('Teardown not confirmed. Retain state and inspect the work request privately.')
            state['deleted']=True;save(a.state,state)
            print('Delete work request succeeded. Verify remaining backups and usage charges before closing paid-run evidence.')
    except (ValueError,TypeError,KeyError,OSError,subprocess.TimeoutExpired):
        p.exit(1,'Lifecycle stopped: check explicit inputs, matching confirmation and private state. No success inferred from an error.\n')


if __name__=='__main__':main()
