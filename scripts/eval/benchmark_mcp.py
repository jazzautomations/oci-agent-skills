#!/usr/bin/env python3
"""Measure the bounded MCP smoke; retain status and timing, never inventory."""
import argparse
import asyncio
from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
import platform
import statistics
import subprocess

from oci_readonly.smoke import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', required=True)
    parser.add_argument('--region', required=True)
    parser.add_argument('--runs', type=int, default=3, choices=range(3, 11))
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    records = []
    for index in range(args.runs):
        try:
            result = asyncio.run(run(True, args.region, 180))
        except Exception:
            result = {'ok': False, 'error': 'run_failed_details_suppressed'}
        records.append(result)
        print(json.dumps({'run': index + 1, 'ok': result['ok']}), flush=True)
    samples = {}
    for record in records:
        for check in record.get('checks', []):
            if 'elapsed_ms' in check:
                key = check['name'] + (':' + check['variant'] if check.get('variant') else '')
                samples.setdefault(key, []).append(check)
    summary = {}
    for key, checks in samples.items():
        times = [check['elapsed_ms'] for check in checks if check['ok']]
        summary[key] = {'attempts': len(checks), 'successes': len(times),
                        'successful_samples_ms': times,
                        'median_ms': statistics.median(times) if times else None,
                        'min_ms': min(times) if times else None,
                        'max_ms': max(times) if times else None}
    report = {
        'date': datetime.now(timezone.utc).isoformat(),
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
        'source_dirty': bool(subprocess.check_output(['git', 'diff', '--', 'runtime/oci_readonly/smoke.py'], cwd=root)),
        'python': platform.python_version(),
        'versions': {name: version(name) for name in ('oci', 'mcp', 'fastmcp', 'oracle-mcp-common')},
        'region': args.region, 'runs': args.runs,
        'method': 'Sequential bounded smoke calls; fresh stdio server per run; no warmup excluded. Each tool is measured once per process. Earlier calls may warm authentication. Public price lookup includes external HTTP. Latency includes transport, client setup, authentication and service time; it is not isolated OCI service latency.',
        'limitations': 'Small sample; no p95 or throughput claim. One region and API-key profile. Empty successful reads validate API access, not deployed workloads. No competitor or model task-completion comparison.',
        'ok': all(record['ok'] for record in records),
        'summary': summary, 'records': records,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
