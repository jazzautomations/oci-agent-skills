#!/usr/bin/env python3
"""Collect isolated semantic selections, or verify dated evidence without model calls.

The model receives descriptions and opaque-id requests only. Exact-match scoring
is deterministic and runs after collection; this is not an end-to-end agent eval.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile

import yaml

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / 'evals/results/semantic.json'
PAIRS = [('R73', 'R74'), ('R75', 'R76'), ('R77', 'R78'), ('R79', 'R80')]


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def inputs(root=ROOT):
    candidates = []
    for path in sorted((root / 'skills').glob('*/SKILL.md')):
        data = yaml.safe_load(path.read_text().split('---', 2)[1])
        candidates.append({'name': data['name'], 'description': data['description']})
    names = [c['name'] for c in candidates]
    if not names or len(names) != len(set(names)):
        raise ValueError('Candidate names must be unique and nonempty')
    files = {name: json.loads((root / 'evals' / name).read_text())
             for name in ['routing.json', 'negatives.json', 'remap.json', 'semantic-policy.json']}
    corpus = json.loads((root / 'evals/corpus/eval-corpus.json').read_text())
    if files['routing.json'] != corpus['routing'] or files['negatives.json'] != corpus['negatives']:
        raise ValueError('Original routing and negative corpus must remain unchanged')
    identifiers = [r['id'] for k in ['routing.json', 'negatives.json'] for r in files[k]]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError('Corpus IDs must be unique')
    policy = files['semantic-policy.json']
    # Do not permit a policy edit to weaken the existing acceptance criteria.
    if (policy['minimum_accuracy'] < .9 or policy['maximum_negative_firings'] != 0
            or policy['required_overlap_pairs'] != 4 or len(set(policy['seeds'])) < 2):
        raise ValueError('Semantic policy weakens acceptance criteria')
    material = {'candidates': candidates, 'corpus': files,
                'collector_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    return candidates, files, digest(material)


def blind_payload(candidates, rows, seed):
    """Whitelist fields before model access; remove R/N prefix, labels and trap metadata."""
    rng = random.Random(seed)
    catalog = [{'name': c['name'], 'description': c['description']} for c in candidates]
    requests = [{'original_id': r['id'], 'prompt': r['prompt']} for r in rows]
    rng.shuffle(catalog)
    rng.shuffle(requests)
    mapping = {f'item{i:03}': r['original_id'] for i, r in enumerate(requests)}
    payload = {'skills': catalog, 'requests': [
        {'id': f'item{i:03}', 'prompt': r['prompt']} for i, r in enumerate(requests)]}
    return payload, mapping


def parse_labels(value, mapping, candidates):
    if not isinstance(value, dict) or set(value) != {'labels'} or not isinstance(value['labels'], list):
        raise ValueError('Expected an object containing only labels')
    valid = {c['name'] for c in candidates}
    selected = {}
    for row in value['labels']:
        if not isinstance(row, dict) or set(row) != {'id', 'skill'}:
            raise ValueError('Invalid label fields')
        identifier, name = row['id'], row['skill']
        if not isinstance(identifier, str) or identifier not in mapping or identifier in selected:
            raise ValueError('Unknown or repeated request ID')
        if name is not None and (not isinstance(name, str) or name not in valid):
            raise ValueError('Unknown skill selection')
        selected[identifier] = name
    if set(selected) != set(mapping):
        raise ValueError('Incomplete prediction set')
    return {mapping[k]: v for k, v in selected.items()}


def score(selected, files):
    remap = files['remap.json']
    rows = files['routing.json']
    correct = {r['id']: selected[r['id']] == remap.get(r['expected_skill'], r['expected_skill']) for r in rows}
    count = sum(correct.values())
    negatives = sum(selected[r['id']] is not None for r in files['negatives.json'])
    overlap = sum(all(correct.get(i, False) for i in pair) for pair in PAIRS)
    policy = files['semantic-policy.json']
    metrics = {'correct': count, 'total': len(rows), 'accuracy': count / len(rows),
               'negative_firings': negatives, 'negative_total': len(files['negatives.json']),
               'overlap_pairs_correct': overlap}
    gates = {'V19': metrics['accuracy'] >= policy['minimum_accuracy'] and overlap == policy['required_overlap_pairs'],
             'V20': negatives == policy['maximum_negative_firings']}
    return {'metrics': metrics, 'gates': gates, 'ok': all(gates.values())}


def parse_transcript(stdout):
    events = [json.loads(line) for line in stdout.splitlines() if line.strip()]
    init = next((e for e in events if e.get('type') == 'system' and e.get('subtype') == 'init'), None)
    result = next((e for e in reversed(events) if e.get('type') == 'result'), None)
    if not init or not result or init.get('tools') or init.get('mcp_servers'):
        raise ValueError('A tool-free initialization and result are required')
    if result.get('is_error') or result.get('subtype') != 'success':
        raise ValueError('Model run did not finish successfully')
    for event in events:
        content = event.get('message', {}).get('content', [])
        if isinstance(content, list) and any(c.get('type') == 'tool_use' for c in content):
            raise ValueError('Tool call observed in classifier-only run')
    if not init.get('model') or not result.get('session_id'):
        raise ValueError('Missing model/session provenance')
    text = result.get('result', '')
    labels = json.loads(text)
    trace = {'model': init['model'], 'session_id': result['session_id'], 'tools': [], 'mcp_servers': [],
             'result': labels, 'duration_ms': result.get('duration_ms'),
             'total_cost_usd': result.get('total_cost_usd'), 'usage': result.get('usage'),
             'model_usage': result.get('modelUsage'), 'num_turns': result.get('num_turns')}
    return labels, trace


def collect(root, report):
    candidates, files, fingerprint = inputs(root)
    policy = files['semantic-policy.json']
    rows = files['routing.json'] + files['negatives.json']
    cli_version = subprocess.check_output(['claude', '--version'], text=True).strip()
    records = []
    for seed in policy['seeds']:
        payload, mapping = blind_payload(candidates, rows, seed)
        argv = ['claude', '--safe-mode', '--setting-sources', '', '--tools', '',
                '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}', '--no-session-persistence',
                '--model', policy['model'], '--max-budget-usd', str(policy['max_budget_usd_per_run']),
                '--output-format', 'stream-json', '--verbose', '--system-prompt', policy['system_prompt'], '-p']
        with tempfile.TemporaryDirectory(prefix='oci-semantic-') as directory:
            env = {k: v for k, v in os.environ.items() if not k.startswith('OCI_') and k != 'CLAUDECODE'}
            env.update(OCI_CONFIG_FILE=str(Path(directory) / 'absent'), OCI_CLI_CONFIG_FILE=str(Path(directory) / 'absent'))
            proc = subprocess.run(argv, input=canonical(payload), text=True, capture_output=True,
                                  cwd=directory, env=env, timeout=policy['timeout_seconds'])
        if proc.returncode:
            raise ValueError('Classifier CLI failed; raw account/provider errors suppressed')
        labels, trace = parse_transcript(proc.stdout)
        if trace['model'] != policy['model']:
            raise ValueError('Resolved model does not match the pinned policy')
        selected = parse_labels(labels, mapping, candidates)
        record = {'seed': seed, 'input_sha256': digest(payload), 'trace': trace, 'score': score(selected, files)}
        records.append(record)
        # Preserve completed trials even if a later call fails; never pick only the best trial.
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps({'complete': False, 'inputs_sha256': fingerprint,
                                      'runs': records}, indent=2) + '\n')
        print(canonical({'seed': seed, **record['score']}), flush=True)
    result = {'version': 1, 'complete': True, 'mode': policy['method'], 'validated_at': datetime.now(timezone.utc).isoformat(),
              'inputs_sha256': fingerprint, 'cli_version': cli_version, 'runs': records,
              'limitations': 'Dated model description selection, not host skill activation or task completion. '
              'Original benchmark is already known to maintainers; not a new unseen holdout. '
              'CLI-reported provenance is not provider attestation. No OCI operations or model tools.',
              'ok': all(r['score']['ok'] for r in records)}
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    return result


def verify(root=ROOT, report=DEFAULT):
    candidates, files, fingerprint = inputs(root)
    policy = files['semantic-policy.json']
    data = json.loads(report.read_text())
    if data.get('complete') is not True or data.get('version') != 1 or data.get('mode') != policy['method'] or data.get('inputs_sha256') != fingerprint:
        raise ValueError('Missing or stale semantic evidence; collect against current inputs')
    if not data.get('cli_version') or not data.get('validated_at'):
        raise ValueError('Missing collection provenance')
    runs = data.get('runs', [])
    if [r.get('seed') for r in runs] != policy['seeds']:
        raise ValueError('Every predeclared trial must be present and ordered')
    sessions, checked = set(), []
    for record in runs:
        payload, mapping = blind_payload(candidates, files['routing.json'] + files['negatives.json'], record['seed'])
        trace = record['trace']
        if record['input_sha256'] != digest(payload) or trace['model'] != policy['model']:
            raise ValueError('Model or request inputs changed')
        session = trace.get('session_id')
        if not session or session in sessions or trace.get('tools') != [] or trace.get('mcp_servers') != []:
            raise ValueError('Invalid isolated trial provenance')
        sessions.add(session)
        scored = score(parse_labels(trace['result'], mapping, candidates), files)
        if scored != record['score']:
            raise ValueError('Reported score differs from recomputed predictions')
        checked.append(scored)
    ok = all(r['ok'] for r in checked)
    if data.get('ok') != ok:
        raise ValueError('Aggregate score differs from recomputed trials')
    return {'mode': 'recorded-semantic-evidence-check', 'validated_at': data['validated_at'],
            'model': policy['model'], 'runs': checked, 'ok': ok,
            'fresh_model_call': False, 'host_task_completion': None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--collect', action='store_true', help='Make the bounded, paid model calls in the policy')
    parser.add_argument('--report', type=Path, default=DEFAULT)
    args = parser.parse_args()
    try:
        result = collect(ROOT, args.report) if args.collect else verify(ROOT, args.report)
        print(json.dumps(result if not args.collect else {'ok': result['ok'], 'report': str(args.report)}, indent=2))
        return 0 if result['ok'] else 1
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        # Do not echo raw provider errors or potentially sensitive subprocess output.
        print(json.dumps({'ok': False, 'error': type(exc).__name__, 'detail': str(exc) if isinstance(exc, ValueError) else 'Collection/evidence validation failed'}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
