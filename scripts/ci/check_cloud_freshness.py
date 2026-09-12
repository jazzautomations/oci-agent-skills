#!/usr/bin/env python3
"""Compare public cloud facts and official reference fingerprints. Never execute page content."""
import argparse
from datetime import datetime,timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[2]
SOURCES={
 'oci_prices':'https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/?currencyCode=USD',
 'oci_cli':'https://pypi.org/pypi/oci-cli/json',
 'oci_sdk':'https://pypi.org/pypi/oci/json',
 'oracledb':'https://pypi.org/pypi/oracledb/json',
 'oci_shapes':'https://docs.oracle.com/en-us/iaas/Content/Compute/References/computeshapes.htm',
 'oci_block_performance':'https://docs.oracle.com/en-us/iaas/Content/Block/Concepts/blockvolumeperformance.htm',
 'oci_migration_support':'https://docs.oracle.com/en-us/iaas/Content/cloud-migration/cloud-migration-requirements-specifications.htm',
 'core_lz_variables':'https://raw.githubusercontent.com/oci-landing-zones/terraform-oci-core-landingzone/main/variables_general.tf',
 'azure_price_contract':'https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices',
 'aws_instance_contract':'https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-instance-types.html',
 'gcp_machine_contract':'https://cloud.google.com/sdk/gcloud/reference/compute/machine-types/describe',
 'oracle_hybrid_search':'https://docs.oracle.com/en/database/oracle/oracle-database/26/vecse/query-hybrid-vector-indexes-end-end-example.html'}
SKUS={'B91628','B93030','B91961','B91962','B97384','B97385','B109529','B109530','B95702','B95706','B110316'}


class PageText(HTMLParser):
    def __init__(self):super().__init__();self.ignore=0;self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'):self.ignore+=1
    def handle_endtag(self,tag):
        if tag in ('script','style'):self.ignore=max(0,self.ignore-1)
    def handle_data(self,data):
        if not self.ignore:self.parts.append(data)


def summarize(name,body):
    if name=='oci_prices':
        data=json.loads(body)
        prices={p['partNumber']:p['currencyCodeLocalizations'] for p in data['items'] if p['partNumber'] in SKUS}
        if prices.keys()!=SKUS:raise ValueError('Incomplete sentinel prices')
        return prices
    if name in {'oci_cli','oci_sdk','oracledb'}:return {'version':json.loads(body)['info']['version']}
    parser=PageText();parser.feed(body)
    text=re.sub(r'\s+',' ',' '.join(parser.parts)).strip()
    if len(text)<100:raise ValueError('Empty reference response')
    if name=='aws_instance_contract':
        # Sphinx repeats the CLI patch release in its title/navigation even when
        # this command's documentation is unchanged. Keep major/minor changes
        # and every version/value in the actual command contract visible.
        text=re.sub(r'\bAWS CLI ([0-9]+\.[0-9]+)\.[0-9]+ Command Reference\b',
                    r'AWS CLI \1.x Command Reference',text)
    return {'content_sha256':hashlib.sha256(text.encode()).hexdigest()}


def collect():
    facts={};gaps=[]
    for name,url in SOURCES.items():
        try:
            request=Request(url,headers={'User-Agent':'oci-agent-skills-freshness/1.0'})
            with urlopen(request,timeout=30) as response:body=response.read(4_000_001)
            if len(body)>4_000_000:raise ValueError('Source too large')
            facts[name]=summarize(name,body.decode('utf-8'))
        except Exception:gaps.append({'source':name,'url':url,'status':'unavailable; not unchanged'})
    return facts,gaps


def compare(previous,current):
    return [{'source':name,'url':SOURCES[name],'previous':previous.get(name),'current':value,
             'review':'Official source changed. Re-read linked documentation, verify assumptions, run affected fixtures and CLI help. Page hashes are signals, not proof of a breaking change.'}
            for name,value in current.items() if previous.get(name)!=value]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--baseline',type=Path,default=ROOT/'catalog/cloud-freshness.json')
    p.add_argument('--write-baseline',action='store_true');p.add_argument('--out',type=Path);a=p.parse_args()
    facts,gaps=collect();now=datetime.now(timezone.utc).isoformat()
    previous=json.loads(a.baseline.read_text()) if a.baseline.exists() else {'facts':{}}
    changed=compare(previous['facts'],facts)
    report={'checked_at':now,'baseline_checked_at':previous.get('checked_at'),'changes':changed,'unavailable':gaps,
      'automatic_actions':'Read fixed public sources only; no cloud mutation, generated code execution, issue posting or automatic baseline acceptance.',
      'scope':'Official cloud docs, price sentinel SKUs and package versions; resource-specific quota/model availability must be read in the target region at run time.'}
    if a.out:a.out.write_text(json.dumps(report,indent=2)+'\n')
    if a.write_baseline:
        if gaps:raise SystemExit('Refusing incomplete baseline; review unavailable sources: '+str(gaps))
        a.baseline.write_text(json.dumps({'checked_at':now,'facts':facts},indent=2,sort_keys=True)+'\n')
    if a.out:a.out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return int(bool(gaps or changed) and not a.write_baseline)


if __name__=='__main__':raise SystemExit(main())
