import importlib.util
import json
from pathlib import Path
import sys
from unittest.mock import Mock, MagicMock
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
    conn=Connection();out=query.query(conn,"' OR 1=1 --",mode='vector')
    sql,binds=conn.cur.calls[0]
    assert binds['q']=="' OR 1=1 --" and "' OR 1=1 --" not in sql
    assert 'FIRST 5' in sql and len(out['untrusted_retrieval'])==1


def test_paid_payload_uses_current_minimum_and_acl():
    p=ctl.create_payload('paid','ocid1.compartment.oc1..example','RAGKIT26','192.0.2.1/32')
    assert p['computeModel']=='ECPU' and p['computeCount']==2 and p['dbVersion']=='26ai'
    with pytest.raises(ValueError):ctl.create_payload('paid','ocid1.compartment.oc1..example','RAGKIT26','0.0.0.0/0')


def test_provision_preserves_id_before_wait_timeout(monkeypatch, tmp_path):
    import oci
    client = Mock()
    client.create_autonomous_database.return_value.data.id = 'synthetic-database'
    monkeypatch.setattr(oci.config, 'from_file', lambda *a: {})
    monkeypatch.setattr(oci.database, 'DatabaseClient', lambda config: client)
    state = {'retry_token': 'same-token', 'owned_demo': True}
    path = tmp_path/'state.json'
    def wait(*args, **kwargs):
        assert json.loads(path.read_text())['adb_id'] == 'synthetic-database'
        raise oci.exceptions.MaximumWaitTimeExceeded('test timeout')
    monkeypatch.setattr(oci, 'wait_until', wait)
    payload = ctl.create_payload('paid', 'ocid1.compartment.oc1..example', 'RAGKIT26', '192.0.2.1/32')
    with pytest.raises(ValueError):
        ctl.provision_database(payload, 'test', 'us-chicago-1', 'same-token', state, path)
    assert client.create_autonomous_database.call_args.kwargs['opc_retry_token'] == 'same-token'
    assert json.loads(path.read_text())['adb_id'] == 'synthetic-database'
    assert path.stat().st_mode & 0o777 == 0o600


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
    p=tmp_path/'setup.sql';p.write_text('-- Instructions mention :unused_password, not an SQL bind.\nBEGIN demo(:model_uri); END;\n/\nSELECT 1 FROM dual\n/\n')
    conn=Connection();setup.apply(conn,p,{'model_uri':'https://example.com/model'})
    assert conn.cur.calls[0][1]=={'model_uri':'https://example.com/model'}
    assert conn.cur.calls[1][1]=={}


def test_setup_accepts_live_26ai_product_branding(monkeypatch):
    import sqlite3
    db = sqlite3.connect(':memory:')
    db.execute('CREATE TABLE product_component_version (product TEXT, version_full TEXT)')
    db.execute('INSERT INTO product_component_version VALUES (?, ?)',
               ('Oracle AI Database 26ai Enterprise Edition ', '23.26.3.2.0'))
    conn = MagicMock()
    cur = conn.cursor.return_value.__enter__.return_value
    def execute(sql, binds=None):
        if sql.startswith('SELECT version_full'):
            cur.fetchone.return_value = db.execute(sql, binds).fetchone()
    cur.execute.side_effect = execute
    context = MagicMock(); context.__enter__.return_value = conn
    monkeypatch.setattr(setup, 'connect', lambda **kwargs: context)
    monkeypatch.setattr(sys, 'argv', ['setup.py', '--grant-mcp', '--execute'])
    setup.main()
    assert cur.fetchone.return_value == ('23.26.3.2.0',)
    assert any(call.args[0].startswith('GRANT READ') for call in cur.execute.call_args_list)
    db.close()


def test_retrieval_benchmark_requires_explicit_execution(monkeypatch, tmp_path, capsys):
    benchmark = module('ragbenchmark', 'benchmark.py')
    monkeypatch.setattr(benchmark, 'connect', lambda: pytest.fail('Unexpected database connection'))
    report = tmp_path/'report.json'
    monkeypatch.setattr(sys, 'argv', ['benchmark.py', '--report', str(report)])
    benchmark.main()
    assert not report.exists()
    assert 'no DB connection' in capsys.readouterr().out


def test_audit_setup_is_admin_only_without_agent_privilege_expansion(monkeypatch):
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value.fetchone.return_value = ('23.26.3.2.0',)
    context = MagicMock(); context.__enter__.return_value = conn
    factory = Mock(return_value=context)
    monkeypatch.setattr(setup, 'connect', factory)
    monkeypatch.setattr(sys, 'argv', ['setup.py', '--audit', '--execute'])
    setup.main()
    factory.assert_called_once_with(admin=True)
    sql = '\n'.join(c.args[0] for c in conn.cursor.return_value.__enter__.return_value.execute.call_args_list)
    assert 'AUDIT POLICY RAG_DEMO_ACCESS BY RAGMCP' in sql
    assert 'GRANT' not in sql


def test_fusion_deduplicates_documents_bounds_output_and_has_no_label_input():
    vector=[('a','a text',.1),('a','duplicate',.2),('b','b text',.3)]
    hybrid=[('b','hybrid text',90),('c','c text',80)]
    rows=query.fuse_documents(vector,hybrid)
    assert [r['document'] for r in rows]==['b','a','c']
    assert rows[0]['rrf_score']==1/62+1/61
    assert len(query.fuse_documents([(str(i),'x'*2000,i) for i in range(10)],[]))==5
    assert all(len(r['chunk'])<=1200 for r in query.fuse_documents(vector,hybrid))


def test_fusion_uses_bound_queries_and_internal_source_attribution():
    conn=Connection();result=query.query(conn,'synthetic question')
    first,second=conn.cur.calls
    assert first[1]=={'q':'synthetic question'}
    assert json.loads(second[1]['request'])['search_text']=='synthetic question'
    assert 'CHARTOROWID' in second[0]
    assert 'rowid' not in result['untrusted_retrieval'][0]
    assert result['retrieval_method']=='document-rrf-k60'


def test_chunk_size_reduction_is_explicit():
    assert '"max":100,"overlap":20' in loader.CHUNK_SQL


def test_relevance_benchmark_dry_run_has_no_database_calls(monkeypatch,tmp_path,capsys):
    b=module('ragrelevance','relevance_benchmark.py')
    monkeypatch.setattr(b,'connect',lambda:pytest.fail('Unexpected connection'))
    monkeypatch.setattr(sys,'argv',['relevance_benchmark.py','--report',str(tmp_path/'out.json')])
    b.main()
    assert 'no database connection' in capsys.readouterr().out
