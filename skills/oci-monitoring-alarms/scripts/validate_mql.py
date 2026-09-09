#!/usr/bin/env python3
'''Validate bounded MQL reads; zero datapoints block review. Never creates an alarm.'''
import argparse
import os
import math
import sys
from datetime import datetime,timedelta
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'scripts'))
from lib.oci_ro import run
from lib.sanitize import emit

def window(start,end):
    a=datetime.fromisoformat(start.replace('Z','+00:00'))
    b=datetime.fromisoformat(end.replace('Z','+00:00'))
    if a.tzinfo is None or b.tzinfo is None or not timedelta(0)<b-a<=timedelta(hours=24):
        raise ValueError('Invalid bounded time window')

def count(rows):
    if not isinstance(rows,list): raise ValueError('Unexpected response')
    total=0
    for row in rows:
        if not isinstance(row,dict) or not isinstance(row.get('points'),list):
            raise ValueError('Unexpected datapoints')
        for point in row['points']:
            if not isinstance(point,dict) or not isinstance(point.get('value'),(int,float)) or isinstance(point.get('value'),bool) or not math.isfinite(point['value']) or not isinstance(point.get('timestamp'),str) or not point['timestamp']:
                raise ValueError('Malformed datapoint')
        total+=len(row['points'])
    return total

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    required=('PROFILE','REGION','COMPARTMENT_ID','METRIC_NAMESPACE','MQL','START_TIME','END_TIME')
    if not all(os.environ.get(k) for k in required): parser.error('Set '+', '.join(required))
    try:window(os.environ['START_TIME'],os.environ['END_TIME'])
    except (ValueError,TypeError): parser.error('Use timezone-aware start/end with 0 < duration <= 24 hours')
    result=run(['monitoring','metric-data','summarize-metrics-data',
                '--compartment-id',os.environ['COMPARTMENT_ID'],'--namespace',os.environ['METRIC_NAMESPACE'],
                '--query-text',os.environ['MQL'],'--start-time',os.environ['START_TIME'],
                '--end-time',os.environ['END_TIME'],'--query','data[].{points:"aggregated-datapoints"}',
                '--no-retry'],profile=os.environ['PROFILE'],region=os.environ['REGION'],sanitize=False)
    try:
        if not result['ok']: raise ValueError('Read failed')
        points=count(result['data'])
    except (ValueError,KeyError,TypeError):
        print(emit({'ok':False,'kind':'failed_or_malformed_read','ready_for_review':False}))
        return 2
    print(emit({'ok':points>0, **({'kind':'no_datapoints'} if not points else {}),
                'datapoints':points,'series':len(result['data']),
                'ready_for_review':points>0,'alarm_created':False,'approved':False}))
    return 0 if points else 1

if __name__=='__main__':
    raise SystemExit(main())
