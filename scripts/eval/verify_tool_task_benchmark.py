"""Verify task inputs, tool receipts and scores without new model or cloud calls."""
import argparse
from collections import Counter
import hashlib,json
import math
from pathlib import Path
import tool_task_benchmark as benchmark
from historical_evidence import verify_historical


def verify(report):
    historical = verify_historical(report, Path(__file__).name, benchmark.ROOT)
    if historical is not None:
        return historical
    tasks={t['id']:t for t in json.loads((benchmark.ROOT/'evals/tasks.json').read_text())}
    fixtures={t['id']:t for t in json.loads((benchmark.ROOT/'evals/tool-task-fixtures.json').read_text())['cases']}
    expected=Counter((case,arm) for case in tasks for arm in benchmark.ARMS)
    if Counter((r['case'],r['arm']) for r in report['results'])!=expected:raise ValueError('Missing/repeated task-arm pair')
    for name,value in report['source_sha256'].items():
        if hashlib.sha256((benchmark.ROOT/name).read_bytes()).hexdigest()!=value:raise ValueError('Source fingerprint changed')
    if report['model']!=benchmark.MODEL or report['effort']!='low' or report['structured_output'] is not True:raise ValueError('Protocol changed')
    for row in report['results']:
        case=fixtures[row['case']]
        if row['input_sha256']!=benchmark.digest(benchmark.payload(tasks[row['case']],case,row['arm'])):raise ValueError('Task/reference input changed')
        if row['completed']:
            allowed={'StructuredOutput','mcp__fixture__read_observation'}
            if set(row['initialized_tools'])-allowed or 'mcp__fixture__read_observation' not in row['initialized_tools']:raise ValueError('Unexpected tool surface')
            if any(c['name'] not in allowed for c in row['tool_calls']):raise ValueError('Unexpected tool use')
            graded=benchmark.grade(case,row['answer'],row['receipts'])
            if any(row[k]!=v for k,v in graded.items()):raise ValueError('Changed score')
            tool_topics=[c['input']['topic'] for c in row['tool_calls'] if c['name']=='mcp__fixture__read_observation']
            if Counter(tool_topics)!=Counter(r['topic'] for r in row['receipts']):raise ValueError('Receipts and model tool calls differ')
        elif row['passed']:raise ValueError('Incomplete attempt cannot pass')
    arms={arm:{'passed':sum(r['passed'] for r in report['results'] if r['arm']==arm),'attempts':40} for arm in benchmark.ARMS}
    complete=all(r['completed'] for r in report['results'])
    if arms!=report['arms'] or complete!=report['complete']:raise ValueError('Aggregate mismatch')
    costs=[r.get('cost_usd') for r in report['results']]
    if any(not isinstance(c,(int,float)) or isinstance(c,bool) or not math.isfinite(c) or c<0 for c in costs):raise ValueError('Missing or invalid cost')
    if not math.isclose(sum(costs),report['reported_cost_usd'],rel_tol=0,abs_tol=1e-9):raise ValueError('Cost aggregate mismatch')
    return {'verified':True,'complete':complete,'arms':arms,'scope':'Original task prompts with structured output and a normalized synthetic read tool; not native host/tool deployments.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('report',type=Path);a=p.parse_args()
    print(json.dumps(verify(json.loads(a.report.read_text())),indent=2))


if __name__=='__main__':main()
