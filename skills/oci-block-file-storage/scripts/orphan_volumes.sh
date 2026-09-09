#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "--help" ]]; then
  printf '%s\n' 'Set PROFILE REGION COMPARTMENT_ID AD. Correlates bounded block/boot attachment samples; hashed candidates only.'
  exit 0
fi
: "${PROFILE:?Set PROFILE}"
: "${REGION:?Set REGION}"
: "${COMPARTMENT_ID:?Set COMPARTMENT_ID}"
: "${AD:?Set AD}"
LIB="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../scripts" && pwd)"
export OCI_STORAGE_LIB="$LIB"
python3 - <<'STORAGE'
import hashlib, json, os, sys
sys.path.insert(0, os.environ['OCI_STORAGE_LIB'])
from lib.oci_ro import run_process
from lib.sanitize import emit
c, ad = os.environ['COMPARTMENT_ID'], os.environ['AD']
base=['--profile',os.environ['PROFILE'],'--region',os.environ['REGION'],'--limit','100','--no-retry']
def fetch(path, extra, query):
    result=run_process(path.split()+['--compartment-id',c]+extra+['--query',query]+base,
                       capture_output=True,text=True,timeout=60)
    if result.returncode: raise ValueError('Read failed')
    rows=json.loads(result.stdout) if result.stdout.strip() else []
    if not isinstance(rows,list): raise ValueError('Unexpected response')
    if len(rows)>=100: raise ValueError('Incomplete sample')
    return rows
try:
    candidates=[]
    for kind,path,attachments,key in [
        ('block','bv volume list','compute volume-attachment list','volume-id'),
        ('boot','bv boot-volume list','compute boot-volume-attachment list','boot-volume-id')]:
        disks=fetch(path,['--availability-domain',ad],'data[].{id:id,state:"lifecycle-state"}')
        extra=['--availability-domain',ad] if kind=='boot' else []
        attached=fetch(attachments,extra,'data[].{volume:"'+key+'",state:"lifecycle-state"}')
        active={r['volume'] for r in attached if r['state']!='DETACHED'}
        for disk in disks:
            if disk['state']=='AVAILABLE' and disk['id'] not in active:
                candidates.append({'kind':kind,'id_sha256':hashlib.sha256(disk['id'].encode()).hexdigest()})
    print(emit({'candidates':candidates,'complete':False,'scope':'same compartment and selected AD; cross-compartment attachments unmeasured'}))
except Exception:
    print(emit({'ok':False,'kind':'failed_or_incomplete_read','candidates':[]}))
    raise SystemExit(1)
STORAGE
