#!/usr/bin/env python3
"""Review or execute sourced schema/index setup on a dedicated demo database."""
import argparse
import json
import os
from pathlib import Path
import re
from urllib.parse import urlparse
from rag_common import connect
ROOT=Path(__file__).resolve().parent


def statements(path):
    return [s.strip() for s in re.split(r'^/\s*$',path.read_text(),flags=re.M) if s.strip()]


def apply(conn,path,binds):
    with conn.cursor() as cur:
        for statement in statements(path):
            executable_lines = '\n'.join(line for line in statement.splitlines()
                                         if not line.lstrip().startswith('--'))
            names=set(re.findall(r':([a-z_]+)\b',executable_lines))
            cur.execute(statement,{k:binds[k] for k in names})


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--admin',action='store_true');p.add_argument('--indexes',action='store_true')
    p.add_argument('--grant-mcp',action='store_true');p.add_argument('--select-ai',action='store_true');p.add_argument('--execute',action='store_true')
    p.add_argument('--audit',action='store_true',help='ADMIN: audit approved demo table SELECT/INSERT for RAGMCP; reconnect the agent afterwards')
    p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    if not a.execute or a.dry_run:
        print('Plan: dedicated ADMIN users' if a.admin else 'Plan: ADMIN object-specific unified auditing' if a.audit else 'Plan: indexes after corpus load' if a.indexes else 'Plan: MCP READ grants' if a.grant_mcp else 'Plan: optional Select AI profile' if a.select_ai else 'Plan: ONNX model and 384-dimension tables')
        print('MUTATING SQL; source-reviewed, database execution pending.');return
    binds={}
    if a.admin:
        for key,env in [('app_password','RAG_PW'),('mcp_password','RAG_MCP_PASSWORD')]:
            pw=os.environ[env]
            if not re.fullmatch(r'[A-Za-z0-9_#@$!%-]{12,30}',pw):p.error('Use a 12..30-character demo password without SQL delimiters')
            binds[key]=pw
    elif not any((a.indexes,a.grant_mcp,a.select_ai,a.audit)):
        uri=os.environ['RAG_MODEL_URI'];parsed=urlparse(uri)
        if parsed.scheme!='https' or not parsed.hostname or not parsed.hostname.endswith(('.oraclecloud.com','.oci.customer-oci.com')):p.error('Use the current Oracle-published HTTPS MiniLM model URI')
        binds['model_uri']=uri
    with connect(admin=a.admin or a.grant_mcp or a.audit) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT version_full FROM product_component_version WHERE product LIKE :product',{'product':'Oracle%Database%'})
            version=cur.fetchone()
            if not version or not str(version[0]).startswith(('23.','26.')):raise ValueError('Verify the provisioned AI Database release before setup')
            if a.grant_mcp:
                for table in ('DOC_TAB', 'DOC_CHUNKS'):
                    cur.execute(f'GRANT READ ON RAGAPP.{table} TO RAGMCP')
                    cur.execute("SELECT COUNT(*) FROM dba_tab_privs WHERE owner='RAGAPP' AND table_name=:table_name AND grantee='RAGMCP' AND privilege='SELECT'", {'table_name': table})
                    if cur.fetchone()[0]:
                        cur.execute(f'REVOKE SELECT ON RAGAPP.{table} FROM RAGMCP')
            elif a.select_ai:
                attrs={'provider':'oci','credential_name':'OCI$RESOURCE_PRINCIPAL','region':os.environ['REGION'],
                  'model':os.environ['RAG_GENAI_MODEL'],'object_list':[{'owner':'RAGAPP','name':'DOC_TAB'},{'owner':'RAGAPP','name':'DOC_CHUNKS'}]}
                # Source: DBMS_CLOUD_AI package; requires separate principal/IAM/quota setup.
                cur.execute("BEGIN DBMS_CLOUD_AI.CREATE_PROFILE(profile_name=>'RAG_DEMO', attributes=>:attrs); END;",{'attrs':json.dumps(attrs)})
            else:apply(conn,ROOT/('admin.sql' if a.admin else 'audit.sql' if a.audit else 'indexes.sql' if a.indexes else 'setup.sql'),binds)
        conn.commit()
    print('Requested SQL completed. Validate embedding dimensions and retrieval before claiming demo success.')


if __name__=='__main__':
    try:main()
    except Exception:raise SystemExit('Setup stopped; inspect grants/model/index state privately. No credentials or raw database errors emitted.')
