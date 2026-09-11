"""One paired regression of the five retained failures; never a full 40-task score."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import subprocess
import tempfile

import checked_task_benchmark as benchmark
from verify_checked_task_benchmark import verify as verify_checked

CASES = ['T01', 'T04', 'T13', 'T23', 'T26']
ROOT = benchmark.ROOT


def source_hash():
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def verify(report):
    if report.get('case_ids') != CASES or report.get('regression_collector_sha256') != source_hash():
        raise ValueError('Regression scope or collector changed')
    if report.get('full_task_certification') is not False or report['budget_usd'] > 1.25:
        raise ValueError('Wrong claim or budget')
    result = verify_checked(report, case_ids=CASES)
    result.update(current_sources=True, case_ids=CASES, full_task_certification=False,
                  scope='Five known failing development cases, one paired attempt each; not 40-task, held-out or live evidence.')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--collect', action='store_true')
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--archive', type=Path)
    args = parser.parse_args()
    if not args.collect:
        print(json.dumps(verify(json.loads(args.report.read_text())), indent=2))
        return 0
    if args.report.exists() or not args.archive or args.archive.exists():
        parser.error('Use new report and private archive paths')
    args.archive.mkdir(parents=True, mode=0o700)
    tasks = {t['id']: t for t in json.loads((ROOT / 'evals/tasks.json').read_text())}
    fixtures = {c['id']: c for c in json.loads((ROOT / 'evals/tool-task-fixtures.json').read_text())['cases']}
    jobs = [(tasks[case], fixtures[case], arm) for case in CASES for arm in benchmark.ARMS]
    random.Random(83).shuffle(jobs)
    report = {'date': datetime.now(timezone.utc).isoformat(), 'case_ids': CASES,
        'regression_collector_sha256': source_hash(), 'full_task_certification': False,
        'model': benchmark.MODEL, 'effort': 'low', 'order_seed': 83, 'runs_per_task_arm': 1,
        'preflight': False, 'source_sha256': benchmark.fingerprints(), 'budget_usd': 1.25,
        'attempt_cap_usd': benchmark.CAP, 'reservation_per_attempt_usd': benchmark.previous.RESERVATION,
        'fresh_copy_symlinks': 0, 'results': [], 'collected_all': False,
        'scope': 'Known failing development cases only. Same checked protocol and original grades; no retries, OCI or execution tools.'}
    with tempfile.TemporaryDirectory(prefix='oci-repair-install-') as directory:
        plugin = Path(directory) / 'plugin'
        subprocess.run(['bash', str(ROOT / 'installers/install.sh'), '--target', str(plugin), '--host', 'claude', '--copy-shared'],
                       check=True, capture_output=True)
        if any(p.is_symlink() for p in plugin.rglob('*')):
            raise ValueError('Unexpected installation symlink')
        with ThreadPoolExecutor(max_workers=2) as pool:
            for offset in range(0, len(jobs), 2):
                if not benchmark.previous.can_admit(report['results'], 2, report['budget_usd']):
                    report['stopped_reason'] = 'Admission budget or missing cost'; break
                for row in pool.map(lambda job: benchmark.attempt(job, plugin, args.archive), jobs[offset:offset + 2]):
                    report['results'].append(row)
                    print(json.dumps({k: row.get(k) for k in ('case', 'arm', 'completed', 'passed', 'cost_usd')}), flush=True)
                report['arms'] = benchmark.previous.original.aggregate(report['results'])
                report['reported_cost_usd'] = sum(r.get('cost_usd') or 0 for r in report['results'])
                report['collected_all'] = len(report['results']) == len(jobs)
                args.report.write_text(json.dumps(report, indent=2) + '\n')
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    return int(not report['collected_all'])


if __name__ == '__main__':
    raise SystemExit(main())
