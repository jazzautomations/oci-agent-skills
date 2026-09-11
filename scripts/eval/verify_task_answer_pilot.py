"""Recompute the paired fixture-answer result locally, without model calls."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import task_answer_pilot as pilot


def verify(report):
    config = json.loads(pilot.FIXTURES.read_text())
    if report['fixture_sha256'] != pilot.digest(config):
        raise ValueError('Fixture changed')
    if report['collector_sha256'] != hashlib.sha256(Path(pilot.__file__).read_bytes()).hexdigest():
        raise ValueError('Collector changed')
    cases = {c['id']: c for c in config['cases']}
    keys = Counter((c['id'], arm, seed) for c in config['cases']
                   for arm in ('with-reference', 'without-reference') for seed in config['seeds'])
    observed = Counter((r['case'], r['arm'], r['order_seed']) for r in report['results'])
    if observed != keys:
        raise ValueError('Missing or repeated attempts')
    for skill, fingerprint in report['skill_sha256'].items():
        if fingerprint != hashlib.sha256((pilot.ROOT/'skills'/skill/'SKILL.md').read_bytes()).hexdigest():
            raise ValueError('Reference changed')
    if set(report['skill_sha256']) != {c['skill'] for c in cases.values()}:
        raise ValueError('Missing reference provenance')
    for row in report['results']:
        case = cases[row['case']]
        if row['input_sha256'] != pilot.digest(pilot.payload(case, row['arm'])):
            raise ValueError('Task input changed')
        if not row['completed']:
            if row['passed']: raise ValueError('Incomplete attempt cannot pass')
            continue
        trace = row['trace']
        if trace['model'] != config['model'] or trace['tools'] != [] or trace['mcp_servers'] != []:
            raise ValueError('Invalid isolated model provenance')
        # JSON comparison distinguishes true from 1, unlike Python dict equality.
        passed = pilot.digest(trace['answer']) == pilot.digest(case['expected'])
        if row['passed'] != passed:
            raise ValueError('Answer score differs')
    expected = pilot.summarize(report['results'], sum(keys.values()))
    if any(report[k] != v for k, v in expected.items()):
        raise ValueError('Aggregate score differs')
    return {'verified': True, **expected, 'scope': 'Recorded fixture answers, not native host/tool execution.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(json.loads(args.report.read_text())), indent=2))


if __name__ == '__main__':
    main()
