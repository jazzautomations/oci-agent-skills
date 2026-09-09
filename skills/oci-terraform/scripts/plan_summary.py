#!/usr/bin/env python3
"""Summarize local plan JSON without values, execution or state changes."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts'))
from lib.oci_ro import check  # Common read-only contract; this helper performs no OCI call.
from lib.sanitize import field, emit
from redact import redact

SENSITIVE_TYPES = ('identity', 'network', 'subnet', 'security', 'route', 'internet_gateway',
                   'nat_gateway', 'service_gateway', 'drg', 'vcn', 'bucket', 'volume',
                   'database', 'autonomous', 'file_system', 'secret', 'key', 'vault')
ACTION_SETS = {('no-op',), ('create',), ('read',), ('update',), ('delete',),
               ('create','delete'), ('delete','create'), ('forget',), ('create','forget')}

def summarize(plan):
    if not isinstance(plan,dict) or not str(plan.get('format_version','')).startswith('1.'):
        raise ValueError('Unsupported plan format')
    changes=plan.get('resource_changes',[])
    if not isinstance(changes,list): raise ValueError('Invalid resource changes')
    counts={'create':0,'read':0,'update':0,'delete':0,'replace':0,'no-op':0,'forget':0}
    review=[]
    for row in changes:
        if not isinstance(row,dict) or not isinstance(row.get('change'),dict):
            raise ValueError('Invalid change')
        actions=row['change'].get('actions')
        if not isinstance(actions,list) or any(not isinstance(x,str) for x in actions):
            raise ValueError('Invalid actions')
        if tuple(actions) not in ACTION_SETS: raise ValueError('Unknown actions')
        address,kind=row.get('address'),row.get('type')
        if not isinstance(address,str) or not isinstance(kind,str):
            raise ValueError('Invalid resource identity')
        replacement='create' in actions and 'delete' in actions
        for action in actions: counts[action]+=1
        if replacement: counts['replace']+=1
        sensitive=any(part in kind for part in SENSITIVE_TYPES)
        if 'delete' in actions or 'forget' in actions or (sensitive and actions!=['no-op']) or row.get('previous_address') or row['change'].get('importing'):
            review.append({'address':field('address',redact(address)),
                           'type':field('type',redact(kind)), 'actions':actions,
                           'replacement':replacement,'sensitive_resource':sensitive,
                           'moved':bool(row.get('previous_address')),
                           'importing':bool(row['change'].get('importing'))})
    return {'source':'local-plan','trust':'account-controlled','ok':True,
            'counts':counts,'review':review,'approval':False,
            'applyable':plan.get('applyable') if isinstance(plan.get('applyable'),bool) else None,
            'complete':plan.get('complete') if isinstance(plan.get('complete'),bool) else None,
            'limit':'Values, outputs and unknowns require separate protected review'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan',help='Local terraform show -json output; never a remote URL')
    args=parser.parse_args()
    try:
        path=Path(args.plan)
        if path.stat().st_size>32*1024*1024: raise ValueError('Plan too large')
        result=summarize(json.loads(path.read_text()))
    except (OSError,ValueError,TypeError,KeyError):
        print(emit({'ok':False,'kind':'invalid_or_unreadable_plan','approval':False}))
        return 1
    print(emit(result))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
