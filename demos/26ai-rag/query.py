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
DOCUMENT_VECTOR_SQL="""SELECT doc_name,chunk_text,distance FROM (
SELECT d.doc_name,c.chunk_text,
VECTOR_DISTANCE(c.embedding,VECTOR_EMBEDDING(ALL_MINILM_L12_V2 USING :q AS DATA),COSINE) distance,
ROW_NUMBER() OVER (PARTITION BY d.id ORDER BY VECTOR_DISTANCE(c.embedding,
VECTOR_EMBEDDING(ALL_MINILM_L12_V2 USING :q AS DATA),COSINE)) rn
FROM doc_chunks c JOIN doc_tab d ON d.id=c.doc_id)
WHERE rn=1 ORDER BY distance FETCH FIRST 5 ROWS ONLY"""
HYBRID_DOCUMENT_SQL="""SELECT d.doc_name,h.chunk_text,h.score
FROM JSON_TABLE(DBMS_HYBRID_VECTOR.SEARCH(JSON(:request)), '$[*]'
COLUMNS(rid VARCHAR2(128) PATH '$.rowid', chunk_text CLOB PATH '$.chunk_text', score NUMBER PATH '$.score')) h
JOIN doc_tab d ON d.rowid=CHARTOROWID(h.rid)
ORDER BY h.score DESC FETCH FIRST 5 ROWS ONLY"""
# https://docs.oracle.com/en-us/iaas/autonomous-database-serverless/doc/dbms-cloud-ai-package.html
AI_SQL="SELECT DBMS_CLOUD_AI.GENERATE(prompt=>:q,profile_name=>'RAG_DEMO',action=>'narrate') FROM dual"


def fuse_documents(vector,hybrid):
    """Equal-weight reciprocal rank fusion; one contribution per document per method."""
    scores={};chunks={}
    for ranking in (vector,hybrid):
        seen=set()
        for name,chunk,_ in ranking:
            if name in seen:continue
            seen.add(name)
            scores[name]=scores.get(name,0)+1/(60+len(seen))
            chunks.setdefault(name,str(text(chunk))[:1200])
    return [{'document':name,'chunk':chunks[name],'rrf_score':scores[name]}
            for name in sorted(scores,key=lambda n:(-scores[n],n))[:5]]


def query(conn,question,mode='fusion'):
    if not 1<=len(question)<=2000:raise ValueError('Question length 1..2000 required')
    if mode not in {'vector','hybrid','fusion','narrate'}:raise ValueError('Unknown retrieval mode')
    with conn.cursor() as cur:
        if mode in {'hybrid','fusion'}:
            payload={'hybrid_index_name':'REFS_HYBRID_IDX','search_text':question,'search_fusion':'INTERSECT','search_scorer':'rsf',
               'vector':{'search_mode':'DOCUMENT','aggregator':'MAX'},'return':{'values':['rowid','score','chunk_text','chunk_id'],'topN':5}}
            vector=[]
            if mode=='fusion':
                cur.execute(DOCUMENT_VECTOR_SQL,{'q':question});vector=cur.fetchmany(5)
            cur.execute(HYBRID_DOCUMENT_SQL,{'request':json.dumps(payload)});hybrid=cur.fetchmany(5)
            if mode=='fusion':return {'untrusted_retrieval':fuse_documents(vector,hybrid),'retrieval_method':'document-rrf-k60'}
            return {'untrusted_retrieval':[{'document':n,'chunk':str(text(c))[:1200],'score':s} for n,c,s in hybrid]}
        if mode=='narrate':
            cur.execute(AI_SQL,{'q':question});return {'untrusted_generated_answer':str(text(cur.fetchone()[0]))[:8000]}
        cur.execute(VECTOR_SQL,{'q':question})
        return {'untrusted_retrieval':[{'document':name,'chunk':str(text(chunk))[:1200],'distance':distance} for name,chunk,distance in cur.fetchmany(5)]}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('question');p.add_argument('--mode',choices=['fusion','vector','hybrid','narrate'],default='fusion')
    p.add_argument('--execute',action='store_true');p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    if not a.execute or a.dry_run:print('Plan: '+a.mode+' query, question bound as data, maximum five retrieval hits. No connection.');return
    with connect() as conn:print(json.dumps(query(conn,a.question,a.mode),indent=2))


if __name__=='__main__':
    try:main()
    except Exception:raise SystemExit('Query failed; no result fabricated. Check dedicated DB, index, grants and optional provider quota.')
