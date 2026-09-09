#!/usr/bin/env python3
'''Read bounded certificate expiry metadata; never retrieve certificate bundles.'''
import argparse
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'scripts'))
from lib.oci_ro import run
from lib.sanitize import emit

def summarize(rows,now,days):
    if not isinstance(rows,list) or len(rows)>=100:
        raise ValueError('Unexpected or incomplete sample')
    result={'sampled':len(rows),'expired':0,'expiring':0,'unknown':0,
            'earliest_expiry':None,'complete':False,'window_days':days}
    dates=[]
    for row in rows:
        try:
            expiry=datetime.fromisoformat(row['expires'].replace('Z','+00:00'))
            if expiry.tzinfo is None: raise ValueError('Missing timezone')
            dates.append(expiry)
            if expiry<=now: result['expired']+=1
            elif expiry<=now+timedelta(days=days): result['expiring']+=1
        except (ValueError,TypeError,KeyError,AttributeError):
            result['unknown']+=1
    if dates: result['earliest_expiry']=min(dates).astimezone(timezone.utc).isoformat()
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--days',type=int,default=30,help='Expiry review window, 0–3650 days')
    args=parser.parse_args()
    if not 0<=args.days<=3650: parser.error('days must be 0–3650')
    if not all(os.environ.get(k) for k in ('PROFILE','REGION','COMPARTMENT_ID')):
        parser.error('Set PROFILE REGION COMPARTMENT_ID after scope verification')
    result=run(['certs-mgmt','certificate','list','--compartment-id',os.environ['COMPARTMENT_ID'],
                '--sort-by','EXPIRATIONDATE','--sort-order','ASC','--limit','100',
                '--query','data.items[].{expires:"current-version-summary".validity."time-of-validity-not-after"}',
                '--no-retry'],profile=os.environ['PROFILE'],region=os.environ['REGION'],sanitize=False)
    try:
        if not result['ok']: raise ValueError('Read failed')
        summary=summarize(result['data'],datetime.now(timezone.utc),args.days)
    except (ValueError,KeyError,TypeError):
        print(emit({'ok':False,'kind':'failed_or_incomplete_read','complete':False}))
        return 2
    print(emit({'ok':True,**summary}))
    return 1 if any(summary[k] for k in ('expired','expiring','unknown')) else 0

if __name__=='__main__':
    raise SystemExit(main())
