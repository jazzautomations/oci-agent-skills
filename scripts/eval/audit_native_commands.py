"""Audit inert native-benchmark proposals against pinned Click metadata; execute none."""
import argparse,hashlib,json,shlex,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from guard_lib import catalog_data,parse_oci,readonly_argv


def metadata():
    import click
    from inventory import load_cli
    cli,errors=load_cli()
    if errors:raise ValueError('Incomplete pinned CLI import')
    aliases={}
    choices={}
    global_options={flag:max(p.opts,key=len) for p in cli.params if isinstance(p,click.Option) for flag in p.opts}
    def walk(command,path):
        if isinstance(command,click.Group):
            for name,child in command.commands.items():walk(child,[*path,name])
        else:
            leaf=' '.join(path)
            aliases[leaf]={**global_options,**{flag:max(p.opts,key=len) for p in command.params if isinstance(p,click.Option) for flag in p.opts}}
            choices[leaf]={max(p.opts,key=len):p.type for p in command.params if isinstance(p,click.Option) and isinstance(p.type,click.Choice)}
    walk(cli,[])
    return aliases,choices


def inspect(command,aliases,choices):
    import jmespath
    try:
        lexer=shlex.shlex(command,posix=True,punctuation_chars=';&|()<>\n')
        lexer.whitespace_split=True
        tokens=list(lexer)
        if any(t in {';','&&','||','|','(',')','>','<','>>','<<'} for t in tokens) or '$(' in command or '\n' in command:
            return {'valid':False,'reason':'shell_composition_or_substitution'}
        argv=shlex.split(command)
        if not argv or argv.pop(0)!='oci':return {'valid':False,'reason':'not_one_oci_command'}
        leaf,raw=parse_oci(argv)
        row=catalog_data()[0].get(leaf)
        if not row or leaf not in aliases:return {'valid':False,'reason':'unknown_leaf'}
        opts={aliases[leaf].get(k,k):v for k,v in raw.items()}
        if len(opts)!=len(raw):return {'valid':False,'reason':'duplicate_alias'}
        if leaf=='raw-request' or not readonly_argv(argv):return {'valid':False,'reason':'not_approved_read'}
        if {'--help','--generate-full-command-json-input','--generate-param-json-input'} & opts.keys():return {'valid':False,'reason':'not_a_read_proposal'}
        if set(row['required'])-opts.keys():return {'valid':False,'reason':'missing_required_option'}
        if '--all' in opts and '--limit' in opts:return {'valid':False,'reason':'all_and_limit_conflict'}
        if row['has_limit'] and '--limit' not in opts:return {'valid':False,'reason':'missing_explicit_limit'}
        if '--query' not in opts:return {'valid':False,'reason':'missing_query'}
        jmespath.compile(opts['--query'])
        for flag,choice in choices.get(leaf,{}).items():
            if flag in opts and '$' not in str(opts[flag]):
                try:choice.convert(opts[flag],None,None)
                except Exception:return {'valid':False,'reason':'invalid_enum_option'}
        return {'valid':True,'reason':'syntax_only','leaf':leaf}
    except Exception:
        return {'valid':False,'reason':'invalid_option_or_query_syntax'}


def main():
    from importlib.metadata import version
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('report',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if version('oci-cli')!='3.93.0':raise ValueError('Use pinned OCI CLI 3.93.0 environment')
    if a.out.exists():raise ValueError('Existing audit preserved')
    report=json.loads(a.report.read_text());aliases,choices=metadata()
    fixtures={c['id']:c for c in json.loads((ROOT/'evals/tool-task-fixtures.json').read_text())['cases']}
    rows=[]
    for row in report['results']:
        commands=row.get('answer',{}).get('commands',[])
        checks=[inspect(c,aliases,choices) for c in commands]
        proposal_ok=(bool(commands) and all(c['valid'] for c in checks)) if fixtures[row['case']]['topic'] else commands==[]
        passed=bool(row.get('completed') and row.get('answer_correct') and row.get('required_evidence_read') and proposal_ok)
        rows.append({'case':row['case'],'arm':row['arm'],'original_passed':row['passed'],'commands':checks,'recomputed_passed':passed})
    out={'source_report_sha256':hashlib.sha256(a.report.read_bytes()).hexdigest(),
         'auditor_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'oci_cli':version('oci-cli'),
         'results':rows,'arms':{arm:{'passed':sum(r['recomputed_passed'] for r in rows if r['arm']==arm),'attempts':sum(r['arm']==arm for r in rows)} for arm in report['arms']},
         'limitations':'Post-collection syntax adjudication, common to both arms: aliases from pinned Click options, no all/limit conflict, compiled JMESPath and literal enum choices using pinned Choice conversion (including case-insensitive OCI enums). Corrects the initial collector rejection of quoted logical operators and acceptance of conflicting flags. Commands and service callbacks are NEVER executed. Query meaning, service callback requirements and workload outcomes remain unmeasured. Original grades are retained, not overwritten.'}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'arms':out['arms'],'changed':sum(r['original_passed']!=r['recomputed_passed'] for r in rows)}))


if __name__=='__main__':raise SystemExit(main())
