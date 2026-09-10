#!/usr/bin/env python3
"""Bounded vector/hybrid retrieval; optional Select AI narrate with explicit setup."""
import argparse
import json
from rag_common import connect,text
# https://docs.oracle.com/en/database/oracle/oracle-database/26/vecse/vector_distance.html
VECTOR_SQL="""SELECT d.doc_name,c.chunk_text,VECTOR_DISTANCE(c.embedding,
VECTOR_EMBEDDING(ALL_MINILM_L12_V2 USING :q AS DATA),COSINE) distance
FROM doc_chunks c JOIN doc_tab d ON d.id=c.doc_id
ORDER BY distance FETCH APPROX FIRST 5 ROWS ONLY"""
# https://docs.oracle.com/en/database/oracle/oracle-database/26/vecse/query-hybrid-vector-indexes-end-end-example.html
HYBRID_SQL='SELECT JSON_SERIALIZE(DBMS_HYBRID_VECTOR.SEARCH(JSON(:request)) RETURNING CLOB) FROM dual'
# https://docs.oracle.com/en-us/iaas/autonomous-database-serverless/doc/dbms-cloud-ai-package.html
AI_SQL="SELECT DBMS_CLOUD_AI.GENERATE(prompt=>:q,profile_name=>'RAG_DEMO',action=>'narrate') FROM dual"


def query(conn,question,mode='vector'):
    if not 1<=len(question)<=2000:raise ValueError('Question length 1..2000 required')
    with conn.cursor() as cur:
        if mode=='hybrid':
            payload={'hybrid_index_name':'REFS_HYBRID_IDX','search_text':question,'search_fusion':'INTERSECT','search_scorer':'rsf',
               'vector':{'search_mode':'DOCUMENT','aggregator':'MAX'},'return':{'values':['score','vector_score','text_score','chunk_text','chunk_id'],'topN':5}}
            cur.execute(HYBRID_SQL,{'request':json.dumps(payload)})
            return {'untrusted_retrieval':json.loads(text(cur.fetchone()[0]))}
        if mode=='narrate':
            cur.execute(AI_SQL,{'q':question});return {'untrusted_generated_answer':str(text(cur.fetchone()[0]))[:8000]}
        cur.execute(VECTOR_SQL,{'q':question})
        return {'untrusted_retrieval':[{'document':name,'chunk':str(text(chunk))[:1200],'distance':distance} for name,chunk,distance in cur.fetchmany(5)]}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('question');p.add_argument('--mode',choices=['vector','hybrid','narrate'],default='vector')
    p.add_argument('--execute',action='store_true');p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    if not a.execute or a.dry_run:print('Plan: '+a.mode+' query, question bound as data, maximum five retrieval hits. No connection.');return
    with connect() as conn:print(json.dumps(query(conn,a.question,a.mode),indent=2))


if __name__=='__main__':
    try:main()
    except Exception:raise SystemExit('Query failed; no result fabricated. Check dedicated DB, index, grants and optional provider quota.')
