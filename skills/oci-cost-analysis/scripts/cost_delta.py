#!/usr/bin/env python3
"""Two settled MONTHLY cost windows, sorted and separated by currency; no FX."""
import argparse
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts'))
from lib.oci_ro import run
from lib.costs import window, rows
from lib.sanitize import emit


def main():
    p=argparse.ArgumentParser(description=__doc__ + ' Set PROFILE REGION TENANCY_ID PRIOR_START PRIOR_END CURRENT_START CURRENT_END.')
    p.parse_args()
    try:
        profile,region,tenancy=(os.environ[k] for k in ('PROFILE','REGION','TENANCY_ID'))
        windows=[window(os.environ[k+'_START'],os.environ[k+'_END'],'MONTHLY',delta=True) for k in ('PRIOR','CURRENT')]
        output=[]
        for start,end in windows:
            result=run(['usage-api','usage-summary','request-summarized-usages','--tenant-id',tenancy,
                        '--time-usage-started',start.isoformat(),'--time-usage-ended',end.isoformat(),
                        '--granularity','MONTHLY','--query-type','COST','--group-by','["service"]','--limit','100'],profile=profile,region=region,sanitize=False)
            if not result['ok']:
                raise ValueError('Usage read failed; no delta calculated')
            output.append(dict(start=start.isoformat(),end=end.isoformat(),rows=rows(result['data'],start,end,monthly=True),
                               truncated=result['truncated'],basis='tenancy rate card; currencies kept separate; no FX'))
        print(emit(output))
    except (KeyError,ValueError):
        p.exit(1,'Cost comparison unavailable: check explicit scope, settled dates, response window and currency.\n')


if __name__=='__main__': main()
