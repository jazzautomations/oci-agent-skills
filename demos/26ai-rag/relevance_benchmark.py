"""Replay fixed development relevance questions against the deployed demo; explicit execution only."""
import argparse
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path
import statistics
from time import perf_counter
from query import query
from rag_common import connect

ROOT=Path(__file__).resolve().parents[2]
FIXTURE=ROOT/'evals/rag-relevance-2026-09-11.json'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--execute',action='store_true');p.add_argument('--report',type=Path,required=True)
    p.add_argument('--mode',choices=['fusion','vector','hybrid'],default='fusion')
    a=p.parse_args()
    if not a.execute:print('Plan: 15 fixed development questions, 3 repetitions; no database connection.');return
    if a.report.exists():raise ValueError('Existing evidence preserved')
    cases=json.loads(FIXTURE.read_text())['cases']
    report={'date':datetime.now(timezone.utc).isoformat(),'mode':a.mode,'fixture_sha256':hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
        'implementation_sha256':{n:hashlib.sha256((Path(__file__).parent/n).read_bytes()).hexdigest() for n in ('query.py','load.py','relevance_benchmark.py')},
        'results':[],'limitations':'Known development queries, including ten fixed before initial second-lab outcomes. Fusion was selected after observing development failures. Expected-source hit@5 is not answer correctness or generalization. Small corpus, sequential calls, no excluded warmup or p95 claim. Fusion uses an exact per-document vector ranking, not a proven HNSW execution plan.'}
    with connect() as conn:
        conn.call_timeout=120000
        with conn.cursor() as cur:
            cur.execute('SELECT COUNT(*) FROM doc_tab');report['documents']=cur.fetchone()[0]
            cur.execute('SELECT COUNT(*) FROM doc_chunks');report['chunks']=cur.fetchone()[0]
            cur.execute("SELECT index_name,status FROM user_indexes WHERE index_name IN ('DOC_CHUNKS_HNSW','REFS_HYBRID_IDX') ORDER BY index_name");report['indexes']=cur.fetchall()
        for case in cases:
            samples=[]
            for trial in range(3):
                start=perf_counter()
                rows=query(conn,case['question'],a.mode)['untrusted_retrieval']
                names=[r['document'] for r in rows]
                samples.append({'run':trial+1,'documents':names,'expected_hit':case['expected'] in names,'elapsed_ms':round((perf_counter()-start)*1000,3)})
            report['results'].append({'case':case['id'],'set':case['set'],'expected':case['expected'],'samples':samples,
                                     'median_ms':statistics.median(r['elapsed_ms'] for r in samples)})
            a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps({'case':case['id'],'successful_queries':len(samples),'expected_hits':sum(r['expected_hit'] for r in samples)}),flush=True)
    report['complete']=True
    report['expected_source_hits']=sum(s['expected_hit'] for r in report['results'] for s in r['samples'])
    report['queries']=sum(len(r['samples']) for r in report['results'])
    a.report.write_text(json.dumps(report,indent=2)+'\n')
    return int(report['expected_source_hits']!=report['queries'])


if __name__=='__main__':raise SystemExit(main())
