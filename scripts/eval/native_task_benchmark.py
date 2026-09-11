"""Paired native Skill activation with synthetic MCP observations and inert CLI proposals."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import hashlib,json,os,random,shlex,subprocess,sys,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from guard_lib import catalog_data,parse_oci,readonly_argv
from tool_task_benchmark import schema,digest,grade

MODEL='claude-sonnet-5'
CAP=0.10
ARMS=('native-plugin','without-plugin')
SYSTEM=('Complete the original task using the closed-world synthetic MCP observations. '
    'If OCI plugin skills are available, invoke a relevant one through the native Skill tool before answering. '
    'Only OCI plugin skills are authorized, never other skills. All resource facts must come from the fixture tool. '
    'The supplied universe is the scoped LAB profile, us-chicago-1, dev compartment or tenancy root as requested. '
    'No real OCI credentials, shell, browsing, file access or cloud writes are authorized. '
    'Return JSON with answer and commands. The answer must match its schema; sort unordered lists alphabetically. '
    'Commands are INERT proposed OCI read commands, not executed evidence. Include at least one relevant read proposal '
    'for a read task, with required options, an output query, and an explicit limit for list commands that support it. '
    'Use quoted shell variables for unknown IDs; never invent real identifiers. For destructive requests require review, '
    'do not execute anything, and return an empty commands list. Never emit shell pipelines or command substitutions.')


def payload(task,fixture):
    output={'type':'object','properties':{'answer':schema(fixture['expected']),
        'commands':{'type':'array','items':{'type':'string'},'maxItems':8}},
        'required':['answer','commands'],'additionalProperties':False}
    return {'request':task['prompt'],'output_schema':output}


def command_check(command):
    """Only inspect syntax; never run model-generated commands, including help."""
    try:
        if any(x in command for x in ('\n','\r','$(', ';','&&','||')):return False
        argv=shlex.split(command)
        if not argv or argv.pop(0)!='oci':return False
        path,options=parse_oci(argv)
        row=catalog_data()[0].get(path)
        if not row or path=='raw-request' or not readonly_argv(argv):return False
        if {'--help','-h','-?','--generate-full-command-json-input','--generate-param-json-input'} & options.keys():return False
        if set(row['required'])-options.keys():return False
        if '--query' not in options:return False
        if row['has_limit'] and '--limit' not in options:return False
        return True
    except (ValueError,TypeError):return False


def score(fixture,answer,receipts):
    if not isinstance(answer,dict) or not isinstance(answer.get('commands'),list):
        return {'answer_correct':False,'required_evidence_read':False,'commands_valid':False,'passed':False}
    base=grade(fixture,answer.get('answer'),receipts)
    commands=answer['commands']
    valid=(1<=len(commands)<=8 and all(isinstance(c,str) and command_check(c) for c in commands)) if fixture['topic'] else commands==[]
    return {**base,'commands_valid':valid,'passed':base['passed'] and valid}


def source_paths():
    return [Path(__file__),Path(__file__).with_name('tool_task_benchmark.py'),
        Path(__file__).with_name('tool_fixture_server.py'),ROOT/'evals/tasks.json',ROOT/'evals/evals.json',
        ROOT/'evals/tool-task-fixtures.json',ROOT/'catalog/cli.jsonl',ROOT/'catalog/cli-meta.json',
        ROOT/'scripts/guard_lib.py',ROOT/'installers/install.py',ROOT/'.claude-plugin/plugin.json',
        ROOT/'.mcp.json',ROOT/'hooks/hooks.json',*sorted((ROOT/'skills').glob('*/SKILL.md'))]


def attempt(job,plugin):
    task,fixture,arm=job
    request=payload(task,fixture)
    row={'case':task['id'],'arm':arm,'input_sha256':digest(request),'completed':False,'passed':False}
    with tempfile.TemporaryDirectory(prefix='oci-native-task-') as directory:
        trace=Path(directory)/'receipts.jsonl'
        config={'mcpServers':{'fixture':{'command':sys.executable,
            'args':[str(plugin/'scripts/eval/tool_fixture_server.py')],
            'env':{'OCI_FIXTURE_TRACE':str(trace)}}}}
        env={k:v for k,v in os.environ.items() if not k.startswith('OCI_') and k not in {'CLAUDECODE','CLAUDE_CODE_SAFE_MODE'}}
        env.update(OCI_CONFIG_FILE=directory+'/absent',OCI_CLI_CONFIG_FILE=directory+'/absent')
        argv=['claude','--restricted','--setting-sources','','--tools','Skill' if arm=='native-plugin' else '',
            '--allowedTools',*(['Skill(oci-agent-skills:*)'] if arm=='native-plugin' else []),'mcp__fixture__read_observation',
            '--strict-mcp-config','--mcp-config',json.dumps(config),'--permission-prompts','none',
            '--no-session-persistence','--model',MODEL,'--effort','low','--max-budget-usd',str(CAP),
            '--json-schema',json.dumps(request['output_schema']),'--output-format','stream-json','--verbose',
            '--system-prompt',SYSTEM,*(['--plugin-dir',str(plugin)] if arm=='native-plugin' else []),'-p']
        try:
            proc=subprocess.run(argv,input=json.dumps(request),cwd=directory,env=env,text=True,capture_output=True,timeout=150)
            events=[json.loads(x) for x in proc.stdout.splitlines() if x.strip()]
            init=next(e for e in events if e.get('type')=='system' and e.get('subtype')=='init')
            result=next(e for e in reversed(events) if e.get('type')=='result')
            contents=[c for e in events for c in e.get('message',{}).get('content',[]) if isinstance(c,dict)]
            outcomes={c['tool_use_id']:not c.get('is_error',False) for c in contents if c.get('type')=='tool_result'}
            calls=[{'name':c['name'],'input':c['input'],'result_success':outcomes.get(c['id'])} for c in contents if c.get('type')=='tool_use']
            receipts=[json.loads(x) for x in trace.read_text().splitlines()] if trace.exists() else []
            row.update(cost_usd=result.get('total_cost_usd'),duration_ms=result.get('duration_ms'),usage=result.get('usage'),
                host_version=init.get('claude_code_version'),model=init.get('model'),result_subtype=result.get('subtype'),
                initialized_tools=init.get('tools'),plugins=[{'name':p['name'],'version':p.get('version')} for p in init.get('plugins',[])],
                plugin_skill_count=sum(s.startswith('oci-agent-skills:') for s in init.get('skills',[])),
                mcp_servers=init.get('mcp_servers'),calls=calls,receipts=receipts)
            allowed={'StructuredOutput','mcp__fixture__read_observation'}|({'Skill'} if arm=='native-plugin' else set())
            if init.get('model')!=MODEL or set(init.get('tools',[]))-allowed:raise ValueError('Tool/model surface')
            if 'mcp__fixture__read_observation' not in init.get('tools',[]):raise ValueError('Fixture tool absent')
            if any(c['name'] not in allowed for c in calls):raise ValueError('Unexpected tool call')
            skill_calls=[c for c in calls if c['name']=='Skill']
            if any(not c['input'].get('skill','').startswith('oci-agent-skills:') for c in skill_calls):raise ValueError('Unexpected skill')
            row['native_skill_activated']=any(c['result_success'] for c in skill_calls)
            if arm=='native-plugin' and (row['plugin_skill_count']!=37 or row['plugins']!=[{'name':'oci-agent-skills','version':'0.2.1'}]):raise ValueError('Native plugin absent')
            if arm=='without-plugin' and row['plugins']:raise ValueError('Baseline contaminated')
            if proc.returncode or result.get('is_error') or result.get('subtype')!='success':raise ValueError('Incomplete attempt')
            answer=result['structured_output']
            row.update(answer=answer,completed=True,**score(fixture,answer,receipts))
        except (ValueError,KeyError,StopIteration,TypeError,OSError,subprocess.TimeoutExpired):
            row['error']='Incomplete or invalid attempt retained without retry.'
    return row


def aggregate(rows):
    return {arm:{'attempts':sum(r['arm']==arm for r in rows),
        'completed':sum(r['arm']==arm and r['completed'] for r in rows),
        'passed':sum(r['arm']==arm and r['passed'] for r in rows),
        'native_activations':sum(r['arm']==arm and r.get('native_skill_activated',False) for r in rows)} for arm in ARMS}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--collect',action='store_true');p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    if not a.collect:print(json.dumps({'attempts':80,'requested_budget_usd':8,'model_calls':0,'cloud_calls':0}));return
    if a.report.exists():raise ValueError('Existing evidence preserved')
    tasks=json.loads((ROOT/'evals/tasks.json').read_text());fixtures={c['id']:c for c in json.loads((ROOT/'evals/tool-task-fixtures.json').read_text())['cases']}
    imported=json.loads((ROOT/'evals/evals.json').read_text())['evals']
    if {t['id']:t['prompt'] for t in tasks}!={t['id']:t['prompt'] for t in imported}:raise ValueError('Original prompt mismatch')
    report={'date':datetime.now(timezone.utc).isoformat(),'model':MODEL,'effort':'low','order_seed':83,'runs_per_task_arm':1,
        'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths()},
        'requested_budget_usd':8,'results':[],
        'scope':'Native installed Skill activation and synthetic MCP observations, paired with no-plugin sessions. CLI proposals are inspected, never executed. No native competitor deployment, live workload, live mutation defense, holdout, or full native plugin-eval claim. Exact answer+receipt+CLI shape grading; query meaning is not independently proven by syntax.'}
    with tempfile.TemporaryDirectory(prefix='oci-native-install-') as directory:
        plugin=Path(directory)/'plugin'
        subprocess.run(['bash',str(ROOT/'installers/install.sh'),'--target',str(plugin),'--host','claude','--copy-shared'],check=True,capture_output=True)
        if any(p.is_symlink() for p in plugin.rglob('*')):raise ValueError('Fresh distribution contains symlinks')
        report['fresh_copy_symlinks']=0
        jobs=[(t,fixtures[t['id']],arm) for t in tasks for arm in ARMS];random.Random(83).shuffle(jobs)
        a.report.parent.mkdir(parents=True,exist_ok=True)
        with ThreadPoolExecutor(max_workers=2) as pool:
            for row in pool.map(lambda job:attempt(job,plugin),jobs):
                report['results'].append(row);report['arms']=aggregate(report['results'])
                report['collected_all']=len(report['results'])==80
                report['all_responses_completed']=all(r['completed'] for r in report['results'])
                report['reported_cost_usd']=sum(r.get('cost_usd') or 0 for r in report['results'])
                a.report.write_text(json.dumps(report,indent=2)+'\n')
                print(json.dumps({k:row.get(k) for k in ('case','arm','completed','passed','native_skill_activated')}),flush=True)
    return int(not report['collected_all'])


if __name__=='__main__':raise SystemExit(main())
