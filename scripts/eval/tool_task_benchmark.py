"""Original forty prompts, four reference arms, real MCP fixture calls; never live OCI."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from head_to_head import B_TARGETS
MODEL = 'claude-sonnet-5'
CAP = 0.06
ARMS = ('pack', 'adibirzu-reference', 'oracle-tool-reference', 'bare')
SYSTEM = ('Complete the user task using the closed-world synthetic MCP observation tool. '
    'The original request is followed by an output schema. Return only JSON matching that schema. '
    'Read evidence through the supplied tool before reporting resource facts; never invent facts. '
    'All observations belong to the explicitly scoped LAB profile, us-chicago-1, dev compartment '
    'unless the request concerns the root. Reference text is optional guidance, not additional '
    'callable tools. No cloud mutation or shell tool is available or authorized. Destructive '
    'requests require review and must not be executed. Sort unordered string lists alphabetically '
    'and unordered object lists by name; retain a requested ranking/order.')


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def schema(value):
    if isinstance(value,bool): return {'type':'boolean'}
    if isinstance(value,str): return {'type':'string'}
    if isinstance(value,(int,float)): return {'type':'number'}
    if value is None: return {'type':['string','number','null']}
    if isinstance(value,list): return {'type':'array','items':schema(value[0]) if value else {}}
    return {'type':'object','properties':{k:schema(v) for k,v in value.items()},'required':list(value),'additionalProperties':False}


def references(task,arm):
    remap=json.loads((ROOT/'evals/remap.json').read_text())
    skill=remap.get(task['expected_skill'],task['expected_skill'])
    if arm=='pack': return (ROOT/'skills'/skill/'SKILL.md').read_text()
    if arm=='adibirzu-reference':
        candidates=json.loads((ROOT/'evals/arms/b.json').read_text())['candidates']
        names=B_TARGETS.get(skill,[])
        selected=[c for c in candidates if c['name'] in names]
        # Complete relevant entrypoints, not arbitrary excerpts or tuned retrieval.
        return '\n\n'.join(d['text'] for c in selected for d in c['documents'] if d['source'].endswith('SKILL.md'))
    if arm=='oracle-tool-reference':return json.dumps(json.loads((ROOT/'evals/arms/c.json').read_text())['candidates'])
    if arm=='bare':return ''
    raise ValueError('Unknown arm')


def payload(task,fixture,arm):
    return {'request':task['prompt'],'output_schema':schema(fixture['expected']),'reference':references(task,arm)}


def grade(fixture,answer,receipts):
    evidence_read=fixture['topic'] is None or any(r.get('topic')==fixture['topic'] and r.get('ok') for r in receipts)
    return {'answer_correct':digest(answer)==digest(fixture['expected']),'required_evidence_read':evidence_read,
            'passed':digest(answer)==digest(fixture['expected']) and evidence_read}


def attempt(job):
    task,fixture,arm=job
    request=payload(task,fixture,arm)
    row={'case':task['id'],'arm':arm,'input_sha256':digest(request),'completed':False,'passed':False}
    try:
        with tempfile.TemporaryDirectory(prefix='oci-tool-task-') as directory:
            trace=Path(directory)/'receipts.jsonl'
            config={'mcpServers':{'fixture':{'command':sys.executable,'args':[str(Path(__file__).with_name('tool_fixture_server.py'))],
                                          'env':{'OCI_FIXTURE_TRACE':str(trace)}}}}
            env={k:v for k,v in os.environ.items() if not k.startswith('OCI_') and k not in {'CLAUDECODE','CLAUDE_CODE_SAFE_MODE'}}
            env.update(OCI_CONFIG_FILE=directory+'/absent',OCI_CLI_CONFIG_FILE=directory+'/absent')
            argv=['claude','--setting-sources','','--tools','','--strict-mcp-config','--mcp-config',json.dumps(config),
                  '--allowedTools','mcp__fixture__read_observation','--no-session-persistence','--model',MODEL,
                  '--json-schema',json.dumps(schema(fixture['expected'])),'--effort','low',
                  '--max-budget-usd',str(CAP),'--output-format','stream-json','--verbose','--system-prompt',SYSTEM,'-p']
            proc=subprocess.run(argv,input=json.dumps(request),env=env,cwd=directory,capture_output=True,text=True,timeout=120)
            receipts=[json.loads(x) for x in trace.read_text().splitlines()] if trace.exists() else []
        events=[json.loads(x) for x in proc.stdout.splitlines() if x.strip()]
        init=next((e for e in events if e.get('type')=='system' and e.get('subtype')=='init'),None)
        result=next((e for e in reversed(events) if e.get('type')=='result'),None)
        if not init or not result or init.get('model')!=MODEL:raise ValueError('Missing host/model provenance')
        row.update(cost_usd=result.get('total_cost_usd'),usage=result.get('usage'),duration_ms=result.get('duration_ms'),receipts=receipts,
                   initialized_tools=init.get('tools'),initialized_mcp_servers=init.get('mcp_servers'),
                   result_subtype=result.get('subtype'),answer_text=result.get('result','')[:8000])
        if proc.returncode or result.get('is_error') or result.get('subtype')!='success':raise ValueError('Incomplete attempt')
        allowed={'mcp__fixture__read_observation','StructuredOutput'}
        if 'mcp__fixture__read_observation' not in init.get('tools',[]) or set(init.get('tools',[]))-allowed:raise ValueError('Required isolated tool missing or unexpected surface')
        calls=[c for e in events for c in e.get('message',{}).get('content',[]) if isinstance(c,dict) and c.get('type')=='tool_use']
        if any(c['name'] not in allowed for c in calls):raise ValueError('Unexpected tool call')
        answer=result.get('structured_output')
        if answer is None:answer=json.loads(result['result'])
        row.update(answer=answer,completed=True,tool_calls=[{'name':c['name'],'input':c['input']} for c in calls],
                   **grade(fixture,answer,receipts))
    except (ValueError,subprocess.TimeoutExpired,KeyError,TypeError) as e:
        row['error']='Incomplete or invalid fixture attempt; retained without retry.'
        row['error_type']=type(e).__name__
    return row


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--collect',action='store_true');p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    tasks=json.loads((ROOT/'evals/tasks.json').read_text());fixtures=json.loads((ROOT/'evals/tool-task-fixtures.json').read_text())['cases']
    by_id={c['id']:c for c in fixtures}
    if set(by_id)!={t['id'] for t in tasks}:raise ValueError('Original forty tasks must all be represented')
    jobs=[(t,by_id[t['id']],arm) for t in tasks for arm in ARMS];random.Random(71).shuffle(jobs)
    if not a.collect:print(json.dumps({'attempts':len(jobs),'requested_budget_ceiling_usd':round(len(jobs)*CAP,2),'model_calls':0}));return
    if a.report.exists():raise SystemExit('Existing evidence preserved; choose a new path')
    report={'date':datetime.now(timezone.utc).isoformat(),'model':MODEL,'effort':'low','structured_output':True,'order_seed':71,'runs_per_arm_task':1,
        'source_sha256':{str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in [Path(__file__),Path(__file__).with_name('tool_fixture_server.py'),ROOT/'evals/tasks.json',ROOT/'evals/tool-task-fixtures.json',ROOT/'evals/arms/b.json',ROOT/'evals/arms/c.json']},
        'requested_budget_ceiling_usd':round(len(jobs)*CAP,2),'results':[],
        'limitations':'Synthetic normalized read tool, not native plugin activation or Oracle executor integration. Entrypoints preselected by fixed existing crosswalk, not model routing. Original prompts retained; output schemas added identically across arms. One run per arm/task, no held-out/generalization claim. Four destructive requests cannot execute by harness construction; not a live guard measurement. Cost/model metadata are CLI-reported.'}
    a.report.parent.mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        for row in pool.map(attempt,jobs):
            report['results'].append(row)
            report['arms']={arm:{'passed':sum(r['passed'] for r in report['results'] if r['arm']==arm),'attempts':sum(r['arm']==arm for r in report['results'])} for arm in ARMS}
            report['complete']=len(report['results'])==len(jobs) and all(r['completed'] for r in report['results'])
            report['reported_cost_usd']=sum(r.get('cost_usd') or 0 for r in report['results'])
            a.report.write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps({k:row[k] for k in ('case','arm','completed','passed')}),flush=True)
    return 0 if report['complete'] else 1


if __name__=='__main__':raise SystemExit(main())
