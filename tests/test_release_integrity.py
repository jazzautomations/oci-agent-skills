"""Release checks preserve evidence and detect secrets without echoing them."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/ci'))
from check_history import scan
from release_gate import diff_evidence


def test_history_includes_identifiers_emails_and_keys():
    value='Author: Person <person@'+'private.test>\n'
    value+='ocid1.tenancy.oc1..'+'a'*24+'\n'
    value+='-----BEGIN '+'PRIVATE KEY-----\n'
    counts=scan(value)
    assert counts['email']==1 and counts['real_ocid']==1 and counts['private_key']==1
    assert not scan('maintainer@example.invalid')['email']


def test_release_diff_does_not_overwrite_baseline(tmp_path,capsys):
    root=tmp_path/'tracked';output=tmp_path/'scratch'
    (root/'docs').mkdir(parents=True);(output/'docs').mkdir(parents=True)
    baseline=root/'docs/validation-matrix.md';baseline.write_text('old\n')
    (output/'docs/validation-matrix.md').write_text('new\n')
    assert diff_evidence(output,root)==['docs/validation-matrix.md']
    assert baseline.read_text()=='old\n'
    assert '-old' in capsys.readouterr().out


def test_saved_judge_scores_apply_explicit_merges():
    import importlib.util
    spec=importlib.util.spec_from_file_location('judge_score',ROOT/'scripts/eval/score_routing_model.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    assert module.score(ROOT/'evals/results/routing-model-this-pack.json')[2] == 78
