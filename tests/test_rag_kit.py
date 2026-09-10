import importlib.util
import json
from pathlib import Path
import sys
from unittest.mock import Mock
import pytest
R=Path(__file__).resolve().parents[1];D=R/'demos/26ai-rag';sys.path.insert(0,str(D))

def module(name,file):
    spec=importlib.util.spec_from_file_location(name,D/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
ctl=module('ragcontrol','control.py');loader=module('ragload','load.py');query=module('ragquery','query.py');setup=module('ragsetup','setup.py')


class Cursor:
    def __init__(self,fail=False):self.calls=[];self.fail=fail
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def execute(self,sql,binds=None):
        self.calls.append((sql,binds))
        if self.fail and sql.startswith('INSERT INTO doc_chunks'):raise RuntimeError('fake connection failure')
    def fetchone(self):return (42,)
    def fetchmany(self,count):return [('reference',"untrusted ' text",.2)]


class Connection:
    def __init__(self,fail=False):self.cur=Cursor(fail);self.commit=Mock();self.rollback=Mock()
    def cursor(self):return self.cur


def test_ingest_replaces_chunks_in_one_transaction_and_binds_text():
    conn=Connection();loader.load(conn,[('reference.md',"text'); DROP TABLE anything; --")])
    assert conn.commit.call_count==1 and conn.rollback.call_count==0
    assert any(sql.startswith('DELETE FROM doc_chunks') for sql,_ in conn.cur.calls)
    assert all('DROP TABLE anything' not in sql for sql,_ in conn.cur.calls)


def test_ingest_failure_rolls_back():
    conn=Connection(True)
    with pytest.raises(RuntimeError):loader.load(conn,[('reference.md','text')])
    conn.rollback.assert_called_once();conn.commit.assert_not_called()


def test_vector_question_is_bound_and_limit_fixed():
    conn=Connection();out=query.query(conn,"' OR 1=1 --")
    sql,binds=conn.cur.calls[0]
    assert binds['q']=="' OR 1=1 --" and "' OR 1=1 --" not in sql
    assert 'FIRST 5' in sql and len(out['untrusted_retrieval'])==1


def test_paid_payload_uses_current_minimum_and_acl():
    p=ctl.create_payload('paid','ocid1.compartment.oc1..example','RAGKIT26','192.0.2.1/32')
    assert p['computeModel']=='ECPU' and p['computeCount']==2 and p['dbVersion']=='26ai'
    with pytest.raises(ValueError):ctl.create_payload('paid','ocid1.compartment.oc1..example','RAGKIT26','0.0.0.0/0')


def test_lifecycle_dry_run_never_executes(monkeypatch,tmp_path,capsys):
    monkeypatch.setattr(ctl.subprocess,'run',lambda *a,**k:pytest.fail('cloud call during dry-run'))
    monkeypatch.setattr(sys,'argv',['control.py','provision','--profile','test','--region','us-chicago-1','--compartment','ocid1.compartment.oc1..example','--acl','192.0.2.1/32','--state',str(tmp_path/'state.json'),'--dry-run'])
    ctl.main();assert not list(tmp_path.iterdir());assert 'MUTATING' in capsys.readouterr().out


def test_teardown_requires_owned_state(monkeypatch,tmp_path):
    monkeypatch.setattr(ctl.subprocess,'run',lambda *a,**k:pytest.fail('unexpected cloud call'))
    monkeypatch.setattr(sys,'argv',['control.py','teardown','--profile','test','--region','us-chicago-1','--state',str(tmp_path/'absent.json'),'--execute'])
    with pytest.raises(SystemExit):ctl.main()


def test_corpus_only_public_paths_and_rejects_symlink(tmp_path):
    (tmp_path/'references').mkdir();(tmp_path/'docs').mkdir();(tmp_path/'docs/skills.md').write_text('catalog')
    (tmp_path/'references/ref.md').symlink_to('/etc/passwd')
    with pytest.raises(ValueError):loader.corpus(tmp_path)


def test_setup_binds_only_relevant_params(tmp_path):
    p=tmp_path/'setup.sql';p.write_text('BEGIN demo(:model_uri); END;\n/\nSELECT 1 FROM dual\n/\n')
    conn=Connection();setup.apply(conn,p,{'model_uri':'https://example.com/model'})
    assert conn.cur.calls[0][1]=={'model_uri':'https://example.com/model'}
    assert conn.cur.calls[1][1]=={}
