"""Tests of eval integrity and failure detection, without OCI or model execution."""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/eval'))
from graders import select, routing, negative, safety


def test_corpus_import_is_unedited():
    source = ROOT / 'research/data/eval-corpus.json'
    if not source.exists():
        import pytest
        pytest.skip('Build-only research checkout absent')
    corpus = json.loads(source.read_text())
    for key, file in [('routing','routing.json'), ('negatives','negatives.json'), ('cases','tasks.json')]:
        assert json.loads((ROOT / 'evals' / file).read_text()) == corpus[key]
    assert {r['id'] for r in corpus['negatives']} == {f'N{i:02}' for i in range(1,41)}


def test_selector_never_uses_expected_labels():
    choices = [{'name':'network', 'description':'VCN subnet route tables'}, {'name':'compute', 'description':'Compute instances shapes resize'}]
    rows = [{'id':'arbitrary', 'prompt':'Resize my OCI compute instance shape', 'expected_skill':'network'}]
    result = routing(rows, choices, {})
    assert result[0]['selected'] == 'compute'
    assert not result[0]['correct']
    assert negative([{'id':'negative', 'prompt':'Resize my OCI compute instance shape'}], choices)[0]['selected'] == 'compute'


def test_safety_grader_detects_silent_drop_and_missing_flags():
    rows = [{'id':'fixture','text':'untrusted'}]
    assert not safety(rows, lambda text: ('', ['flag']))[0]['pass']
    assert not safety(rows, lambda text: ('untrusted', []))[0]['pass']


def test_all_task_shapes_preserve_prompts():
    import yaml
    cases = json.loads((ROOT / 'evals/tasks.json').read_text())
    alternate = json.loads((ROOT / 'evals/evals.json').read_text())['evals']
    for row, alt in zip(cases, alternate):
        case = yaml.safe_load((ROOT / 'evals/cases' / row['id'] / 'case.yaml').read_text())
        assert case['prompt'] == alt['prompt'] == row['prompt']
