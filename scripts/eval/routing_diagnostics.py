#!/usr/bin/env python3
"""Expose case-level errors in verified semantic evidence; never recollect or relabel."""
import argparse
import hashlib
import json
from pathlib import Path

import semantic


def diagnose(root=semantic.ROOT, report=semantic.DEFAULT):
    verified = semantic.verify(root, report)
    candidates, files, fingerprint = semantic.inputs(root)
    evidence = json.loads(report.read_text())
    predictions = []
    for run in evidence['runs']:
        _, mapping = semantic.blind_payload(
            candidates, files['routing.json'] + files['negatives.json'], run['seed'])
        predictions.append((run['seed'], semantic.parse_labels(
            run['trace']['result'], mapping, candidates)))

    routing, negatives = [], []
    consistent = correct_every_trial = 0
    for corpus, errors in [('routing.json', routing), ('negatives.json', negatives)]:
        for row in files[corpus]:
            expected = (files['remap.json'].get(row['expected_skill'], row['expected_skill'])
                        if corpus == 'routing.json' else None)
            selections = [{'seed': seed, 'selected': selected[row['id']],
                           'correct': selected[row['id']] == expected}
                          for seed, selected in predictions]
            same = len({s['selected'] for s in selections}) == 1
            if corpus == 'routing.json':
                consistent += same
                correct_every_trial += all(s['correct'] for s in selections)
            failures = [s['seed'] for s in selections if not s['correct']]
            if failures:
                errors.append({'id': row['id'], 'prompt': row['prompt'],
                               'expected': expected, 'selections': selections,
                               'failing_seeds': failures, 'same_selection_in_all_trials': same})

    return {
        'version': 1, 'mode': 'verified-semantic-error-analysis',
        'evidence_sha256': hashlib.sha256(report.read_bytes()).hexdigest(),
        'semantic_inputs_sha256': fingerprint,
        'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'validated_at': verified['validated_at'], 'model': verified['model'],
        'minimum_accuracy': files['semantic-policy.json']['minimum_accuracy'],
        'evidence_valid': True, 'gates_pass': verified['ok'],
        'perfect_routing': not routing, 'routing_total': len(files['routing.json']),
        'negative_total': len(files['negatives.json']),
        'routing_correct_in_every_trial': correct_every_trial,
        'routing_same_selection_in_every_trial': consistent,
        'trials': [{'seed': run['seed'], **run['score']['metrics']} for run in evidence['runs']],
        'routing_errors': routing, 'negative_errors': negatives,
        'limitations': 'Known development corpus; agreement is not correctness. '
                       'This diagnostic does not adjudicate disputed labels, change gates, '
                       'or measure native host task completion.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, default=semantic.DEFAULT)
    output = parser.add_mutually_exclusive_group()
    output.add_argument('--json', type=Path, help='Save the diagnostic report')
    output.add_argument('--check', type=Path, help='Verify a saved diagnostic against current inputs')
    args = parser.parse_args()
    try:
        result = diagnose(report=args.report)
        if args.check and json.loads(args.check.read_text()) != result:
            raise ValueError('Stale or inconsistent routing diagnostics')
        rendered = json.dumps(result, indent=2, ensure_ascii=False) + '\n'
        if args.json:
            args.json.write_text(rendered)
        print(rendered, end='')
        return 0 if result['gates_pass'] else 1
    except (OSError, ValueError, KeyError, TypeError):
        print(json.dumps({'evidence_valid': False, 'error': 'Unavailable or inconsistent evidence'}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
