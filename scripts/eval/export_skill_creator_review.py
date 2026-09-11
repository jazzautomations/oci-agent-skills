"""Export recorded paired evidence to the upstream skill-creator review format.

No inference, model-generated execution, cloud calls or feedback-server startup.
Use a separately downloaded, pinned anthropics/skills skill-creator directory.
This format adapter does not certify the broader V27 rubric by itself.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

from verify_native_reference_benchmark import verify

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM_COMMIT = '34040c9c568585f6929bedeaad110ad08f079624'
UPSTREAM_FILES = {
    'scripts/aggregate_benchmark.py': '123ef128ea5ccc01a4b1ac212ef5567f21e9c13d3d240609780beeb3200c49aa',
    'eval-viewer/generate_review.py': 'fc9d1b9243fe5ab6012ebd579bd76d0035de1b79fd3b969de114defab26478fb',
    'eval-viewer/viewer.html': 'a53213426ee1100441d701a3a0d49cda7a842f992d2c36463f4d3cc0258575fa',
}
EXPECTATION = 'Original fixture answer, required observation receipt and pinned CLI syntax all pass.'


def total_tokens(usage):
    # Includes cache input rather than mislabeling output character count as tokens.
    return sum(usage.get(key, 0) for key in (
        'input_tokens', 'output_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens'))


def grading(row, audit):
    passed = bool(audit['recomputed_passed'])
    evidence = {'completed': row['completed'], 'answer_correct': row.get('answer_correct', False),
                'required_evidence_read': row.get('required_evidence_read', False),
                'command_checks': audit['commands'], 'original_passed': row['passed']}
    return {
        'expectations': [{'text': EXPECTATION, 'passed': passed, 'evidence': json.dumps(evidence, sort_keys=True)}],
        'summary': {'passed': int(passed), 'failed': int(not passed), 'total': 1, 'pass_rate': int(passed)},
        'execution_metrics': {'tool_calls': dict(Counter(c['name'] for c in row['calls'])),
                              'total_tool_calls': len(row['calls']), 'errors_encountered': int(not row['completed'])},
        # Upstream aggregator reads actual token counts from sibling timing.json.
        'claims': [
            {'claim': 'Native Skill activated', 'type': 'process', 'verified': row['native_skill_activated'],
             'evidence': 'Successful Skill tool-result receipts only; not inferred from answer quality.'},
            {'claim': 'Referenced files were read', 'type': 'process', 'verified': row['successful_reference_reads'] > 0,
             'evidence': f"{row['successful_reference_reads']} successful Read calls inside allowed trees."}],
        'user_notes_summary': {'uncertainties': ['Query meaning and service callbacks are not proven by syntax.'],
                               'needs_review': ['One development-corpus repetition; no held-out or native competitor claim.'],
                               'workarounds': []},
        'eval_feedback': {'suggestions': ['Independently adjudicate original task semantics before claiming the V27 rubric.'],
                         'overall': 'One conjunctive assertion per task avoids inflating scores with easy subchecks.'},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('audit', type=Path)
    parser.add_argument('--upstream-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        parser.error('Use an absent output directory; preserve prior reviews')
    report = json.loads(args.report.read_text())
    verify(report)
    audit = json.loads(args.audit.read_text())
    if audit['source_report_sha256'] != hashlib.sha256(args.report.read_bytes()).hexdigest():
        raise ValueError('Audit belongs to another report')
    # Independently recompute the audit beforehand with verify_native_command_audit.py.
    if audit['auditor_sha256'] != hashlib.sha256((ROOT / 'scripts/eval/audit_native_commands.py').read_bytes()).hexdigest():
        raise ValueError('Auditor changed')
    expected_pairs = Counter((r['case'], r['arm']) for r in report['results'])
    if Counter((r['case'], r['arm']) for r in audit['results']) != expected_pairs:
        raise ValueError('Audit pair mismatch')
    for name, expected in UPSTREAM_FILES.items():
        if hashlib.sha256((args.upstream_dir / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Upstream file differs from pinned reviewed source')
    tasks = {t['id']: t for t in json.loads((ROOT / 'evals/tasks.json').read_text())}
    audited = {(r['case'], r['arm']): r for r in audit['results']}
    args.output_dir.mkdir(parents=True)
    for row in report['results']:
        task = tasks[row['case']]
        config = 'with_skill' if row['arm'] == 'native-plugin' else 'without_skill'
        eval_dir = args.output_dir / f"eval-{int(row['case'][1:]):02d}"
        run = eval_dir / config / 'run-1'
        (run / 'outputs').mkdir(parents=True)
        metadata = {'eval_id': int(row['case'][1:]), 'eval_name': task['name'],
                    'prompt': task['prompt'], 'assertions': [EXPECTATION]}
        # Viewer looks at the run or its immediate parent; aggregator at eval dir.
        for directory in (eval_dir, run):
            (directory / 'eval_metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
        (run / 'outputs/answer.json').write_text(json.dumps(row.get('answer'), indent=2) + '\n')
        (run / 'outputs/observed-tool-calls.json').write_text(json.dumps(row['calls'], indent=2) + '\n')
        (run / 'grading.json').write_text(json.dumps(grading(row, audited[(row['case'], row['arm'])]), indent=2) + '\n')
        (run / 'timing.json').write_text(json.dumps({
            'total_duration_seconds': row['duration_ms'] / 1000,
            'wall_duration_seconds': row['wall_duration_seconds'],
            'total_tokens': total_tokens(row['usage']), 'cost_usd': row['cost_usd'],
        }, indent=2) + '\n')
    spec = importlib.util.spec_from_file_location('pinned_aggregate', args.upstream_dir / 'scripts/aggregate_benchmark.py')
    aggregator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(aggregator)
    summary = aggregator.generate_benchmark(args.output_dir, 'oci-agent-skills', 'skills/')
    # Correct upstream placeholder defaults from captured evidence, not guessed values.
    summary['metadata'].update(executor_model=report['model'], analyzer_model='deterministic-recorded-evidence',
                               timestamp=report['date'], runs_per_configuration=1,
                               upstream_commit=UPSTREAM_COMMIT,
                               source_report_sha256=audit['source_report_sha256'],
                               audit_sha256=hashlib.sha256(args.audit.read_bytes()).hexdigest())
    summary['notes'] = [report['scope'],
        'Pass-rate dispersion is across different tasks, not repeated-run uncertainty or statistical significance.',
        'The paired comparison changes the plugin bundle and Read availability together; it does not isolate the causal effect of references.',
        'Exact schema/fixture grading can reject semantically reasonable text; original results and failures remain unchanged.',
        'Official aggregation/viewer format alone does not establish V27, V28 or a 100% release claim.']
    (args.output_dir / 'benchmark.json').write_text(json.dumps(summary, indent=2) + '\n')
    (args.output_dir / 'benchmark.md').write_text(aggregator.generate_markdown(summary) + '\n')
    subprocess.run([sys.executable, str(args.upstream_dir / 'eval-viewer/generate_review.py'),
                    str(args.output_dir), '--skill-name', 'oci-agent-skills', '--benchmark',
                    str(args.output_dir / 'benchmark.json'), '--static', str(args.output_dir / 'review.html')], check=True)
    print(json.dumps({'runs': len(summary['runs']), 'run_summary': summary['run_summary']}))


if __name__ == '__main__':
    main()
