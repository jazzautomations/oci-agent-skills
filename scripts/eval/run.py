#!/usr/bin/env python3
"""Run deterministic description, negative, fence and guard proxies offline.

This is not an agent benchmark: no model completion, tool execution or live
injection is measured. Exit nonzero if a requested numerical gate is missed.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'scripts/ci'), str(Path(__file__).parent)]
import yaml
import lint_fences
from guard_lib import inspect_command
from lib.sanitize import clean
from graders import routing, negative, safety, select


def read(name):
    return json.loads((ROOT / 'evals' / name).read_text())


def candidates(root=ROOT):
    result = []
    for path in sorted((root / 'skills').glob('*/SKILL.md')):
        if path.parent.name.startswith('_'):
            continue
        metadata = yaml.safe_load(path.read_text().split('---', 2)[1])
        result.append({'name': metadata['name'], 'description': metadata['description'], 'path': str(path)})
    return result


def commands(choices):
    output = []
    documents = set()
    import re
    for choice in choices:
        path = Path(choice['path'])
        documents.add(path)
        documents.update((path.parent / 'references').glob('*.md'))
        for reference in re.findall(r'(?:\.\./)*references/[A-Za-z0-9_.-]+\.md', path.read_text()):
            target = (path.parent / reference).resolve()
            if target.is_file() and target.is_relative_to(ROOT):
                documents.add(target)
    for document in sorted(documents):
        findings = lint_fences.validate(document)
        by_line = {f['line']: f['code'] for f in findings}
        for line, _ in lint_fences.commands(document.read_text()):
            output.append({'source': str(document.relative_to(ROOT)), 'line': line, 'valid': line not in by_line, 'finding': by_line.get(line)})
    return output


def run():
    choices = candidates()
    route = routing(read('routing.json'), choices, read('remap.json'))
    negatives = negative(read('negatives.json'), choices)
    fences = commands(choices)
    injected = safety(read('safety.json'), clean)
    replay = []
    for fixture in read('guard-replay.json'):
        for repetition in range(5):
            decision = inspect_command(fixture['command'])
            replay.append({'id': fixture['id'], 'run': repetition + 1, 'decision': decision})
    tasks = []
    for case in read('tasks.json'):
        selected = select(case['prompt'], choices)
        selected_fences = [f for f in fences if selected and ('skills/' + selected + '/') in f['source']]
        tasks.append({'id': case['id'], 'selected': selected, 'fences_checked': len(selected_fences),
                      'command_validity': sum(f['valid'] for f in selected_fences) / len(selected_fences) if selected_fences else None,
                      'task_completion': None, 'reason': 'Static retrieval only; no agent transcript.'})
    accuracy = sum(r['correct'] for r in route) / len(route)
    false_positives = sum(r['selected'] is not None for r in negatives)
    valid = sum(r['valid'] for r in fences) / len(fences) if fences else 0
    overlap = sum(all(next(r for r in route if r['id'] == name)['correct'] for name in pair) for pair in [('R73','R74'),('R75','R76'),('R77','R78'),('R79','R80')])
    auto_allowed = sum(row['decision'] == 'allow' for row in replay)
    gates = {'V19': accuracy >= 0.9 and overlap == 4, 'V20': false_positives == 0,
             'command_validity': valid >= 0.95, 'guard_replay': auto_allowed == 0,
             'sanitizer': all(r['pass'] for r in injected)}
    return {'mode': 'offline-static-proxy', 'model': None, 'temperature': None, 'runs': 1,
            'threshold': 0.8, 'agent_task_score': None,
            'limitations': 'Description retrieval is not host routing. Fences are authored examples, not generated commands. Guard replay is not mutation execution. Sanitizer checks cannot prove task completion, scope preservation, leakage, silent-drop or over-refusal behavior.',
            'metrics': {'routing_accuracy': accuracy, 'routing_count': len(route), 'overlap_pairs_correct': overlap,
                        'negative_firings': false_positives, 'negative_count': len(negatives),
                        'fenced_command_validity': valid, 'fenced_command_count': len(fences),
                        'guard_auto_allowed': auto_allowed, 'guard_replays': len(replay),
                        'safety_strings_passed': sum(r['pass'] for r in injected),
                        'description_characters': sum(len(c['description']) for c in choices)},
            'gates': gates, 'ok': all(gates.values()), 'routing': route, 'negatives': negatives,
            'commands': fences, 'tasks': tasks, 'safety': injected, 'guard_replay': replay}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', type=Path)
    parser.add_argument('--negatives', action='store_true')
    args = parser.parse_args()
    result = run()
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('mode', 'metrics', 'gates', 'ok')}, indent=2))
    return int(not result['gates']['V20'] if args.negatives else not result['ok'])


if __name__ == '__main__':
    raise SystemExit(main())
