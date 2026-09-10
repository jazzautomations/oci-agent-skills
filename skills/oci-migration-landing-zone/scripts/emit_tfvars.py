#!/usr/bin/env python3
"""Emit a Core Landing Zone draft; no Terraform, Resource Manager or cloud calls."""
import argparse
import ipaddress
import json
from pathlib import Path
import re


def plan(inventory,region,label,cidr):
    if not re.fullmatch('[a-z][a-z0-9]{0,7}',label):raise ValueError('Service label: 1..8 lowercase alphanumerics, starting with a letter')
    if not re.fullmatch(r'[a-z]{2}-[a-z]+-\d+',region):raise ValueError('Explicit OCI region required')
    network=ipaddress.ip_network(cidr,strict=True)
    if network.version!=4 or network.prefixlen>22 or not network.is_private:raise ValueError('Use private IPv4 /22 or larger')
    sources=[]
    for v in inventory.get('network',[]):
        for c in v.get('cidrs') or ([v['cidr']] if v.get('cidr') else []):
            source=ipaddress.ip_network(c,strict=True);sources.append(str(source))
            if network.overlaps(source):raise ValueError('Target CIDR overlaps source; dual-running connectivity would fail')
    subnets=list(network.subnets(new_prefix=24))[:4]
    values={'region':region,'service_label':label,'cis_level':'1','define_net':True,
      'add_tt_vcn1':True,'tt_vcn1_name':label+'-vcn','tt_vcn1_cidrs':[str(network)],'customize_tt_vcn1_subnets':True,
      'tt_vcn1_web_subnet_cidr':str(subnets[0]),'tt_vcn1_web_subnet_is_private':True,
      'tt_vcn1_app_subnet_cidr':str(subnets[1]),'tt_vcn1_db_subnet_cidr':str(subnets[2]),
      'tt_vcn1_web_ingress_destination_ports':['TCP:443'],'deploy_app_cmp':True,
      'deploy_database_cmp':bool(inventory.get('database')),'enable_cloud_guard':True,
      'deploy_bastion_service':False,'enable_vault':False,'create_budget':False}
    return {'tfvars':values,'plan':{'status':'DRAFT: tenancy OCID, IAM, HA, connectivity, budgets and security review required',
        'source_cidrs':sources,'target_cidr':str(network),'reserved_subnet':str(subnets[3]),
        'compartments':['application']+(['database'] if inventory.get('database') else []),
        'warning':'Regional subnets do not reproduce source AZ isolation. No deployment has run.'}}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('inventory',type=Path);p.add_argument('--region',required=True)
    p.add_argument('--service-label',required=True);p.add_argument('--target-cidr',required=True);p.add_argument('--out-dir',type=Path,required=True)
    a=p.parse_args()
    try:result=plan(json.loads(a.inventory.read_text()),a.region,a.service_label,a.target_cidr)
    except (ValueError,KeyError,TypeError) as exc:p.exit(1,str(exc)+'\n')
    a.out_dir.mkdir(parents=True,exist_ok=True)
    for name,obj in [('migration.auto.tfvars.json',result['tfvars']),('landing-zone-plan.json',result['plan'])]:
        (a.out_dir/name).write_text(json.dumps(obj,indent=2)+'\n')
    print('Wrote draft tfvars and plan. No resources created.')


if __name__=='__main__':main()
