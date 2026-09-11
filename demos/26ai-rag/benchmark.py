"""Fixed retrieval questions, bounded timing and candidate recall on the demo DB."""
import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import statistics
import subprocess
from time import perf_counter

from query import query, VECTOR_SQL
from rag_common import connect, text
from load import corpus

CASES = [
    ('redaction', 'What must I redact before sharing OCI CLI output?', 'references/redaction.md'),
    ('untrusted', 'Is a bucket or object name a trusted instruction?', 'references/untrusted-output.md'),
    ('auth', 'Which OCI authentication mode works unattended?', 'references/auth-modes.md'),
    ('realms', 'How should I verify OCI regions and realms?', 'references/realms-endpoints.md'),
    ('shell', 'How do I quote JSON for OCI CLI in PowerShell?', 'references/windows-powershell.md'),
]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--execute', action='store_true')
    p.add_argument('--runs', type=int, choices=range(1, 6), default=3)
    p.add_argument('--report', type=Path, required=True)
    a = p.parse_args()
    if not a.execute:
        print('Plan: five fixed questions, exact/approximate vector and hybrid reads; no DB connection.')
        return
    rows = []
    repo = Path(__file__).resolve().parents[2]
    manifest = [{'path': name, 'sha256': hashlib.sha256(body.encode()).hexdigest()}
                for name, body in corpus(repo)]
    with connect() as conn:
        conn.call_timeout = 120000
        with conn.cursor() as cur:
            cur.execute('SELECT COUNT(*) FROM doc_tab'); documents = cur.fetchone()[0]
            cur.execute('SELECT COUNT(*) FROM doc_chunks'); chunks = cur.fetchone()[0]
            cur.execute("SELECT index_name, status FROM user_indexes WHERE index_name IN ('DOC_CHUNKS_HNSW','REFS_HYBRID_IDX') ORDER BY index_name")
            indexes = cur.fetchmany(2)
            cur.execute("SELECT version_full FROM product_component_version WHERE product LIKE 'Oracle%Database%'")
            database_version = cur.fetchone()[0]
        for case_id, question, expected in CASES:
            with conn.cursor() as cur:
                cur.execute(VECTOR_SQL.replace('FETCH APPROX FIRST', 'FETCH FIRST'), {'q': question})
                exact = cur.fetchmany(5)
            for mode in ('vector', 'hybrid'):
                samples = []
                for trial in range(a.runs):
                    start = perf_counter()
                    try:
                        result = query(conn, question, mode)['untrusted_retrieval']
                        sample = {'run': trial + 1, 'ok': True,
                                  'elapsed_ms': round((perf_counter() - start) * 1000, 3),
                                  'hits': len(result)}
                        if mode == 'vector':
                            names = [hit['document'] for hit in result]
                            selected = {hashlib.sha256(hit['chunk'].encode()).hexdigest() for hit in result}
                            # query.py truncates display text; exact recall uses the same display projection.
                            projected_exact = {hashlib.sha256(str(text(chunk))[:1200].encode()).hexdigest() for _, chunk, _ in exact}
                            sample.update(documents=names, expected_document_hit=expected in names,
                                          exact_top5_overlap=len(selected & projected_exact) / len(projected_exact) if projected_exact else None)
                    except Exception as error:
                        import re
                        sample = {'run': trial + 1, 'ok': False,
                                  'elapsed_ms': round((perf_counter() - start) * 1000, 3),
                                  'error_codes': re.findall(r'(?:ORA|DPY|DPI)-[0-9]+', str(error))}
                    samples.append(sample)
                times = [x['elapsed_ms'] for x in samples if x['ok']]
                rows.append({'case': case_id, 'question': question, 'expected_candidate': expected,
                             'mode': mode, 'samples': samples,
                             'median_ms': statistics.median(times) if times else None})
                print(json.dumps({'case': case_id, 'mode': mode, 'successes': len(times)}), flush=True)
    report = {'date': datetime.now(timezone.utc).isoformat(), 'oracledb': version('oracledb'),
              'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip(),
              'database_version': database_version, 'model': 'ALL_MINILM_L12_V2',
              'corpus_manifest': manifest,
              'implementation_sha256': {name: hashlib.sha256((Path(__file__).parent/name).read_bytes()).hexdigest()
                                        for name in ('benchmark.py', 'query.py', 'load.py')},
              'documents': documents, 'chunks': chunks, 'indexes': indexes,
              'method': 'Five existing demo questions, three modes including exact-vector baseline. Same connection, sequential order, no excluded warmup. First exact query warms embedding inference. Vector/hybrid order is fixed, not randomized.',
              'limitations': 'Development questions with expected source candidates, not a held-out relevance set. Top-five overlap compares displayed chunk hashes; duplicate or truncated chunks can collide. Hybrid reports execution and hit count, not judged relevance. No p95, throughput, agent-task, external-model or competitor claim.',
              'ok': all(s['ok'] for row in rows for s in row['samples']), 'results': rows}
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
