"""Release checks preserve evidence and detect secrets without echoing them."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/ci'))
from check_history import scan
from release_gate import diff_evidence, reference_task_status


def history_patch(body, *, old='a'*40, new='b'*40):
    lines = body.splitlines()
    added = sum(line.startswith(('+', ' ')) for line in lines)
    removed = sum(line.startswith(('-', ' ')) for line in lines)
    return ('commit fixture\ndiff --git a/file b/file\nindex ' + old + '..' + new +
            ' 100644\n--- a/file\n+++ b/file\n@@ -1,' + str(removed) + ' +1,' + str(added) + ' @@\n' + body)


def test_history_includes_identifiers_emails_and_keys_only_in_patch_bodies():
    address = 'person@' + 'private.test'
    body = '+Author: Person <' + address + '>\n'
    body += '+ocid1.tenancy.oc1..' + 'a'*24 + '\n'
    body += '+-----BEGIN ' + 'PRIVATE KEY-----\n'
    counts = scan(history_patch(body))
    assert counts['email'] == 1 and counts['real_ocid'] == 1 and counts['private_key'] == 1
    assert not scan(history_patch('+maintainer@example.invalid\n'))['email']


def test_history_exempts_commit_identities_messages_and_trailers():
    address = 'person@' + 'private.test'
    metadata = ('commit fixture\nAuthor: Person <' + address + '>\nCommit: Person <' + address + '>\n'
                '    Co-Authored-By: Person <' + address + '>\n    Claude-Session: ' + address + '\n')
    assert not any(scan(metadata + history_patch('+safe\n') + metadata).values())
    # Trailer-looking text written into a file is still content, not Git metadata.
    assert scan(history_patch('+Co-Authored-By: ' + address + '\n'))['email'] == 1


def test_history_hunk_content_cannot_masquerade_as_diff_headers():
    address = 'person@' + 'private.test'
    assert scan(history_patch('-' + address + '\n+++ ' + address + '\n'))['email'] == 2
    headers = history_patch('+safe\n').replace('a/file', 'a/' + address).replace('b/file', 'b/' + address)
    assert not scan(headers)['email']


def test_history_reports_original_blob_for_deletions_without_matches():
    from check_history import inspect
    address = 'person@' + 'private.test'
    counts, locations = inspect(history_patch('-' + address + '\n+safe\n'))
    assert counts['email'] == 1
    assert locations == [{'commit':'fixture', 'side':'removed', 'file':'file',
                          'blob':'a'*40, 'counts':{'email':1}}]
    assert address not in str(locations)


def test_history_scanner_against_a_real_temporary_git_history(tmp_path, monkeypatch, capsys):
    import json
    import subprocess
    import check_history
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=tmp_path, stderr=subprocess.PIPE, text=True).strip()
    git('init', '-q')
    git('config', 'user.name', 'Synthetic Author')
    git('config', 'commit.gpgsign', 'false')
    address = 'person@' + 'private.test'
    git('config', 'user.email', address)
    path = tmp_path/'sample.txt'
    path.write_text('safe\n')
    git('add', 'sample.txt')
    git('-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'Initial\n\nCo-Authored-By: ' + address)
    path.write_text(address + '\n')
    git('add', 'sample.txt')
    git('-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'Add synthetic fixture')
    offending = git('rev-parse', 'HEAD:sample.txt')
    path.write_text('safe\n')
    git('add', 'sample.txt')
    git('-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'Remove fixture\n\nClaude-Session: ' + address)
    monkeypatch.setattr(check_history, 'ROOT', tmp_path)
    assert check_history.main() == 1
    output = capsys.readouterr().out
    report = json.loads(output)
    assert report['counts']['email'] == 2
    assert {row['blob'] for row in report['locations']} == {offending}
    assert {row['side'] for row in report['locations']} == {'added', 'removed'}
    assert address not in output


def test_history_location_redacts_sensitive_path_components():
    from check_history import inspect
    address = 'person@' + 'private.test'
    history = history_patch('+' + address + '\n').replace('b/file', 'b/' + address)
    counts, locations = inspect(history)
    assert counts['email'] == 1
    assert address not in str(locations)
    assert locations[0]['file'] == '<redacted>'


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


def test_reference_score_below_threshold_fails_but_high_score_is_not_full_certificate():
    assert reference_task_status({'arms': {'native-plugin': {'attempts': 40, 'passed': 29}}}) == 'FAIL'
    assert reference_task_status({'arms': {'native-plugin': {'attempts': 40, 'passed': 40}}}) == 'PARTIAL'
