import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/eval'))
import tool_task_benchmark as benchmark
import verify_tool_task_benchmark as verifier
import pytest


def test_original_forty_tasks_covered_without_replacing_prompts():
    tasks=json.loads((ROOT/'evals/tasks.json').read_text())
    fixtures=json.loads((ROOT/'evals/tool-task-fixtures.json').read_text())['cases']
    assert len(tasks)==len(fixtures)==40
    assert {x['id'] for x in tasks}=={x['id'] for x in fixtures}
    for task,fixture in zip(tasks,fixtures):
        assert task['id']==fixture['id']
        p=benchmark.payload(task,fixture,'bare')
        assert p['request']==task['prompt']
        assert 'expected' not in p and 'observation' not in p


def test_correct_answer_without_required_tool_receipt_fails():
    case={'topic':'identity','expected':{'user':'lab-user'}}
    assert benchmark.grade(case,case['expected'],[])['passed'] is False
    assert benchmark.grade(case,case['expected'],[{'topic':'identity','ok':True}])['passed'] is True
    assert benchmark.grade(case,{'user':'invented'},[{'topic':'identity','ok':True}])['passed'] is False


def test_schema_does_not_publish_expected_values():
    result=benchmark.schema({'count':17,'name':'private-fixture-value','enabled':True})
    assert result['properties']=={'count':{'type':'number'},'name':{'type':'string'},'enabled':{'type':'boolean'}}
    assert '17' not in json.dumps(result) and 'private-fixture-value' not in json.dumps(result)


def test_all_reference_arms_have_predeclared_entrypoints():
    tasks=json.loads((ROOT/'evals/tasks.json').read_text())
    for task in tasks:
        assert benchmark.references(task,'pack')
        assert benchmark.references(task,'adibirzu-reference')
        assert benchmark.references(task,'oracle-tool-reference')
        assert benchmark.references(task,'bare')==''


def test_recorded_tool_benchmark_verifies_without_new_model_calls():
    report=json.loads((ROOT/'evals/results/tool-task-benchmark-structured-2026-09-11.json').read_text())
    result=verifier.verify(report)
    assert result['verified'] is True
    assert result['complete'] is False  # Six budget-limited attempts remain failures.
    assert result['arms']['pack']=={'passed':39,'attempts':40}


def test_recorded_tool_benchmark_rejects_missing_receipt_and_changed_score():
    original=json.loads((ROOT/'evals/results/tool-task-benchmark-structured-2026-09-11.json').read_text())
    for mutation in ('receipt','score'):
        report=json.loads(json.dumps(original))
        row=next(r for r in report['results'] if r['passed'] and r['receipts'])
        if mutation=='receipt':row['receipts']=[]
        else:row['passed']=False
        with pytest.raises(ValueError):verifier.verify(report)
