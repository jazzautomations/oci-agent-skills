"""Thin TLS connection and bounded output. Credentials come only from environment."""
import os


def connect(admin=False):
    import oracledb
    dsn=os.environ['RAG_DSN']
    if 'tcps' not in dsn.lower() or 'ssl_server_dn_match=no' in dsn.lower():
        raise ValueError('Use the server-authenticated TLS descriptor with DN matching')
    user='ADMIN' if admin else os.environ.get('RAG_USER','RAGAPP')
    if not admin and user!='RAGAPP':raise ValueError('Use the dedicated RAGAPP user')
    return oracledb.connect(user=user,password=os.environ['RAG_ADMIN_PASSWORD' if admin else 'RAG_PW'],dsn=dsn,ssl_server_dn_match=True)


def text(value): return value.read() if hasattr(value,'read') else value
