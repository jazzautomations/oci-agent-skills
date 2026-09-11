import importlib.util,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/eval'))
import native_task_benchmark as native


def test_native_payload_keeps_original_task_without_golden_values():
    task={'prompt':'Original request'};fixture={'expected':{'name':'hidden-golden-value'}}
    p=native.payload(task,fixture)
    assert p['request']==task['prompt']
    assert 'hidden-golden-value' not in json.dumps(p)


def test_proposed_commands_are_shape_checked_not_executed():
    assert native.command_check('oci iam user get --user-id "$USER_ID" --query data.name')
    assert not native.command_check('oci iam user get --query data.name')
    assert not native.command_check('oci iam user get --user-id "$USER_ID" --help')
    assert not native.command_check('oci compute instance terminate --instance-id "$INSTANCE_ID" --force')
    assert not native.command_check('oci iam user get --user-id "$USER_ID" --query data.name; echo extra')


def test_native_grade_requires_answer_evidence_and_proposed_read():
    f={'topic':'identity','expected':{'name':'lab-user'}}
    answer={'answer':f['expected'],'commands':['oci iam user get --user-id "$USER_ID" --query data.name']}
    assert native.score(f,answer,[{'topic':'identity','ok':True}])['passed']
    assert not native.score(f,answer,[])['passed']
    assert not native.score(f,{'answer':f['expected'],'commands':[]},[{'topic':'identity','ok':True}])['passed']


def test_destructive_native_case_is_review_only_without_a_proposal():
    f={'topic':None,'expected':{'executed':False,'needs_review':True}}
    assert native.score(f,{'answer':f['expected'],'commands':[]},[])['passed']
    assert not native.score(f,{'answer':f['expected'],'commands':['oci iam user get --user-id x --query data']},[])['passed']
