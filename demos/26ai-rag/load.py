#!/usr/bin/env python3
"""Idempotently load public repository docs and embed in-database; dry-run by default."""
import argparse
from pathlib import Path
from rag_common import connect
# https://docs.oracle.com/en/database/oracle/oracle-database/26/vecse/utl_to_embeddings-dbms_vector_chain.html
CHUNK_SQL="""INSERT INTO doc_chunks(doc_id,chunk_offset,chunk_text,embedding)
SELECT d.id, e.embed_id, e.embed_data, TO_VECTOR(e.embed_vector)
FROM doc_tab d,
  DBMS_VECTOR_CHAIN.UTL_TO_EMBEDDINGS(
    DBMS_VECTOR_CHAIN.UTL_TO_CHUNKS(d.text, JSON('{"by":"words","max":300,"overlap":40,"split":"recursively","normalize":"all","language":"american"}')),
    JSON('{"provider":"database","model":"ALL_MINILM_L12_V2"}')) t,
  JSON_TABLE(t.column_value, '$[*]' COLUMNS(embed_id NUMBER PATH '$.embed_id',
    embed_data VARCHAR2(4000) PATH '$.embed_data', embed_vector CLOB PATH '$.embed_vector')) e
WHERE d.id=:doc_id"""


def corpus(root):
    files=sorted((root/'references').glob('*.md'))+[root/'docs/skills.md']
    result=[]
    for path in files:
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):raise ValueError('Corpus must stay inside repo')
        text=path.read_text()
        if len(text.encode())>1_000_000:raise ValueError('Corpus document too large')
        result.append((path.relative_to(root).as_posix(),text))
    return result


def load(conn,documents):
    """One transaction per corpus run; rollback restores the previous chunks on any error."""
    try:
        with conn.cursor() as cur:
            for name,body in documents:
                cur.execute('SELECT id FROM doc_tab WHERE doc_name=:name',{'name':name});existing=cur.fetchone()
                if existing:
                    doc_id=existing[0]
                    cur.execute('DELETE FROM doc_chunks WHERE doc_id=:id',{'id':doc_id})
                    cur.execute('UPDATE doc_tab SET text=:body WHERE id=:id',{'body':body,'id':doc_id})
                else:
                    cur.execute('INSERT INTO doc_tab(doc_name,text) VALUES (:name,:body)',{'name':name,'body':body})
                    cur.execute('SELECT id FROM doc_tab WHERE doc_name=:name',{'name':name});doc_id=cur.fetchone()[0]
                cur.execute(CHUNK_SQL,{'doc_id':doc_id})
        conn.commit()
    except Exception:
        conn.rollback();raise


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2])
    p.add_argument('--execute',action='store_true');p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    docs=corpus(a.repo)
    if not a.execute or a.dry_run:print(f'Plan: {len(docs)} public documents, {sum(len(t.encode()) for _,t in docs)} bytes; ONNX 384 dimensions, 300-word chunks. No database connection.');return
    with connect() as conn:load(conn,docs)
    print('Corpus load committed. Create/synchronize indexes and measure retrieval separately.')


if __name__=='__main__':
    try:main()
    except Exception:raise SystemExit('Load failed; transaction rolled back. Inspect the dedicated database privately.')
