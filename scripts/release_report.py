#!/usr/bin/env python3
"""Reproduce published package counts, guard matrix, denylist comparisons and token estimates."""
import asyncio
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / 'runtime'))
from oci_readonly.server import mcp
from guard_lib import classify_leaf


def main():
    leaves=[json.loads(line) for line in (ROOT/'catalog/cli.jsonl').read_text().splitlines()]
    skills=[yaml.safe_load(p.read_text().split('---',2)[1]) for p in sorted((ROOT/'skills').glob('*/SKILL.md'))]
    tools=asyncio.run(mcp.list_tools())
    desc=sum(len(s['description']) for s in skills)
    schemas=len(json.dumps([t.model_dump(exclude_none=True) for t in tools],separators=(',',':')))
    denied=[line for line in (ROOT/'evals/arms/oracle-denylist.txt').read_text().splitlines() if line and not line.startswith('#')]
    current=Counter((r['kind'],'denied' if any(r['path']==s or r['path'].startswith(s+' ') for s in denied) else 'allowed') for r in leaves)
    historical=json.loads((ROOT/'docs/evidence/denylist-coverage-research.json').read_text())
    unowned={'marketplace-publisher','marketplace-private-offer','costad','demand-signal','mngdmac','cpg','dif','gdp','ccc','psa','ddfs'}
    services=Counter(r['path'].split()[0] for r in leaves)
    report={'skills':len(skills),'description_characters':desc,'description_tokens_estimate':(desc+3)//4,
        'mcp_tools':[t.name for t in tools], 'mcp_schema_tokens_estimate':(schemas+3)//4,
        'host_context_measurement':json.loads((ROOT/'docs/evidence/context-measurement.json').read_text()),
        'independent_guard_matrix':json.loads((ROOT/'docs/evidence/guard-severity-matrix.json').read_text()),
        'raw_estimate_method':'ceil(description characters / 4) + ceil(serialized MCP schema characters / 4); excludes host framing',
        'resident_tokens_estimate':(desc+3)//4+(schemas+3)//4,
        'published_planning_floor':'≈6.3–6.5k tokens (≈3,020 descriptions + ≈3,300–3,500 MCP schemas, estimates)',
        'examples':len(json.loads((ROOT/'catalog/examples.json').read_text())['examples']),
        'cli_leaves':len(leaves),'cli_groups':len(services),
        'guard_matrix':{'/'.join(k):v for k,v in sorted(Counter((r['kind'],classify_leaf(r['path'])) for r in leaves).items())},
        'critical_denied':sum(r['severity']=='CRITICAL' and classify_leaf(r['path'])=='deny' for r in leaves),
        'oracle_historical':{'entries':historical['denylist_entries'],'destructive_allowed':historical['stats']['destructive_allowed'], 'mutating_allowed':historical['mutating_not_denied_count'], 'reads_denied':sum(r['kind']=='read' for r in leaves)-historical['stats']['read_allowed'], 'source':'research/data/denylist-coverage.json, shipped as docs/evidence/denylist-coverage-research.json; historical matching/classification differs from current prefix replay'},
        'oracle_current_prefix_replay':{'/'.join(k):v for k,v in sorted(current.items())},
        'historical_certification_counts':json.loads((ROOT/'docs/evidence/certification-coverage-research.json').read_text())['reported_counts'],
        'unowned_services':{name:services[name] for name in sorted(unowned)},
        'unowned_leaves':sum(services[name] for name in unowned),
        'live_cli_statuses':dict(Counter(r['status'] for r in json.loads((ROOT/'docs/evidence/validation-cli.json').read_text())['checks']))}
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
