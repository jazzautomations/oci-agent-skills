"""Replay allowlisted immutable reports with their original offline verifier.

No report-selected code, network fetch, model call or cloud operation is allowed.
Changing current skills must not rewrite earlier measurements into new evidence.
"""
from functools import lru_cache
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[2]
COMMIT = '0cd2730f8677de909267db57baf8a135458646b2'
REPAIR_COMMIT = 'eafde851d370a165ce9ef2dcbd4f9c9126a5fbac'
COMMITS = {COMMIT, REPAIR_COMMIT}
VERIFIERS = {'verify_native_task_benchmark.py', 'verify_native_reference_benchmark.py',
             'verify_checked_task_benchmark.py', 'verify_tool_task_benchmark.py',
             'verify_task_answer_pilot.py', 'task_repair_regression.py'}


def digest(report):
    return hashlib.sha256(json.dumps(report, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


@lru_cache(maxsize=2)
def snapshot(root, revision=COMMIT):
    """Keep the temporary owner alive until process exit; never mutate the checkout."""
    if revision not in COMMITS:
        raise ValueError('Historical revision is not allowlisted')
    try:
        archive = subprocess.run(['git', 'archive', '--format=tar', revision], cwd=root,
                                 capture_output=True, check=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError('Historical verification needs the full source Git checkout') from exc
    owner = tempfile.TemporaryDirectory(prefix='oci-evidence-snapshot-')
    with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
        if any(not (m.isfile() or m.isdir()) for m in bundle.getmembers()):
            owner.cleanup()
            raise ValueError('Snapshot contains a non-regular entry')
        bundle.extractall(owner.name, filter='data')
    return owner, Path(owner.name)


def context_paths(report, tree):
    paths = set(report.get('source_sha256', {}))
    paths.update('skills/' + name + '/SKILL.md' for name in report.get('skill_sha256', {}))
    # Older normalized/pilot payloads embed skill bodies but do not enumerate
    # every one in source_sha256. Include them conservatively for currentness.
    paths.update(str(p.relative_to(tree)) for p in (tree / 'skills').glob('*/SKILL.md'))
    if 'collector_sha256' in report:
        paths.update({'scripts/eval/task_answer_pilot.py', 'evals/task-answer-pilot.json'})
    if 'regression_collector_sha256' in report:
        paths.add('scripts/eval/task_repair_regression.py')
    return sorted(paths)


def changed_sources(report, root, tree):
    return [name for name in context_paths(report, tree)
            if not (root / name).is_file() or (root / name).read_bytes() != (tree / name).read_bytes()]


@lru_cache(maxsize=16)
def replay(root_name, report_path, verifier, revision=COMMIT):
    root = Path(root_name)
    if verifier not in VERIFIERS:
        raise ValueError('Verifier is not allowlisted')
    _, tree = snapshot(root_name, revision)
    environment = {k: v for k, v in os.environ.items() if not k.startswith('OCI_')}
    environment.update(OCI_CONFIG_FILE=str(tree / 'absent'), OCI_CLI_CONFIG_FILE=str(tree / 'absent'),
                       PYTHONPATH=os.pathsep.join((str(tree / 'scripts'), str(tree / 'runtime'))))
    arguments = ['--report'] if verifier == 'task_repair_regression.py' else []
    process = subprocess.run([sys.executable, str(tree / 'scripts/eval' / verifier), *arguments, str(tree / report_path)],
                             cwd=tree, env=environment, capture_output=True, text=True, timeout=90)
    if process.returncode:
        raise ValueError('Original offline verifier rejected historical evidence')
    return json.loads(process.stdout)


def verify_historical(report, verifier, root=ROOT):
    """Unknown or modified reports fall through to strict current-source checks."""
    if verifier not in VERIFIERS:
        raise ValueError('Verifier is not allowlisted')
    registry = json.loads((root / 'evals/historical-evidence.json').read_text())
    record = registry['reports'].get(digest(report))
    if record is None:
        return None
    revision = record.get('commit', registry['commit'])
    if registry['commit'] != COMMIT or revision not in COMMITS or record['verifier'] != verifier:
        raise ValueError('Historical provenance changed')
    _, tree = snapshot(str(root), revision)
    path = Path(record['path'])
    if path.is_absolute() or '..' in path.parts or path.parts[:2] != ('evals', 'results'):
        raise ValueError('Invalid historical report path')
    if digest(json.loads((tree / path).read_text())) != digest(report):
        raise ValueError('Report differs from the immutable revision')
    result = dict(replay(str(root), str(path), verifier, revision))
    changes = changed_sources(report, root, tree)
    result.update(evidence_revision=revision, current_sources=not changes, changed_sources=changes,
                  historical_replay=True, executed_model_commands=0, model_calls=0, cloud_calls=0)
    return result
