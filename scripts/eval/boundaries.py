#!/usr/bin/env python3
"""Additional synthetic scope regressions; never described as an unseen holdout."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

import semantic

ROOT = semantic.ROOT
REPORT = ROOT / 'evals/results/semantic-boundaries.json'


def context():
    candidates, files, fingerprint = semantic.inputs()
    cases = json.loads((ROOT / 'evals/semantic-boundaries.json').read_text())
    payload, mapping = semantic.blind_payload(candidates, cases['cases'], 43)
    binding = semantic.digest({'semantic_inputs': fingerprint, 'cases': cases,
                              'collector': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    return candidates, files['semantic-policy.json'], cases, payload, mapping, binding


def grade(labels, mapping, candidates, cases):
    selected = semantic.parse_labels(labels, mapping, candidates)
    errors = [r['id'] for r in cases['cases'] if selected[r['id']] != r['expected_skill']]
    return {'correct': len(cases['cases']) - len(errors), 'total': len(cases['cases']),
            'errors': errors, 'ok': not errors}


def collect(report):
    candidates, policy, cases, payload, mapping, binding = context()
    argv = ['claude', '--safe-mode', '--setting-sources', '', '--tools', '',
            '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}', '--no-session-persistence',
            '--model', policy['model'], '--max-budget-usd', '0.25', '--output-format', 'stream-json',
            '--verbose', '--system-prompt', policy['system_prompt'], '-p']
    with tempfile.TemporaryDirectory(prefix='oci-boundaries-') as directory:
        env = {k: v for k, v in os.environ.items() if not k.startswith('OCI_') and k != 'CLAUDECODE'}
        env.update(OCI_CONFIG_FILE=str(Path(directory) / 'absent'), OCI_CLI_CONFIG_FILE=str(Path(directory) / 'absent'))
        result = subprocess.run(argv, input=semantic.canonical(payload), capture_output=True,
                                text=True, env=env, cwd=directory, timeout=120)
    if result.returncode:
        raise ValueError('Boundary collection failed; provider output suppressed')
    labels, trace = semantic.parse_transcript(result.stdout)
    if trace['model'] != policy['model']:
        raise ValueError('Resolved model differs from policy')
    data = {'mode': 'synthetic-semantic-boundaries', 'validated_at': datetime.now(timezone.utc).isoformat(),
            'inputs_sha256': binding, 'request_sha256': semantic.digest(payload), 'trace': trace,
            'provenance': cases['provenance'], 'score': grade(labels, mapping, candidates, cases)}
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    return data['score']


def verify(report=REPORT):
    candidates, policy, cases, payload, mapping, binding = context()
    data = json.loads(report.read_text())
    trace = data['trace']
    if (data['inputs_sha256'] != binding or data['request_sha256'] != semantic.digest(payload)
            or trace['model'] != policy['model'] or not trace.get('session_id')
            or trace.get('tools') != [] or trace.get('mcp_servers') != []):
        raise ValueError('Missing, stale or invalid boundary evidence')
    score = grade(trace['result'], mapping, candidates, cases)
    if score != data['score']:
        raise ValueError('Incorrect boundary score')
    return score


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--collect', action='store_true')
    parser.add_argument('--report', type=Path, default=REPORT)
    args = parser.parse_args()
    try:
        result = collect(args.report) if args.collect else verify(args.report)
        print(json.dumps(result))
        return 0 if result['ok'] else 1
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
        print(json.dumps({'ok': False, 'error': 'Boundary evidence unavailable or invalid'}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
