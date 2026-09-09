#!/usr/bin/env python3
"""Measure host prompt framing with an identical, bounded no-tool-call A/B prompt."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import tempfile

PROMPT = 'Reply with exactly OK. Do not call any tools.'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plugin-dir',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args()
    rows=[]
    version=subprocess.check_output(['claude','--version'],text=True).strip()
    with tempfile.TemporaryDirectory(prefix='oci-host-framing-') as directory:
        environment=dict(os.environ,OCI_CONFIG_FILE=str(Path(directory)/'absent'),OCI_CLI_CONFIG_FILE=str(Path(directory)/'absent'))
        base=['claude','-p',PROMPT,'--output-format','stream-json','--verbose','--permission-prompts','none',
              '--setting-sources','','--no-session-persistence','--strict-mcp-config','--mcp-config','{"mcpServers":{}}']
        for name,extra in [('base',[]),('plugin',['--plugin-dir',str(args.plugin_dir.resolve())])]:
            try:
                result=subprocess.run(base+extra,cwd=directory,env=environment,capture_output=True,text=True,timeout=90)
                events=[json.loads(line) for line in result.stdout.splitlines() if line.startswith('{')]
                initialized=next(e for e in events if e.get('type')=='system' and e.get('subtype')=='init')
                completed=next(e for e in events if e.get('type')=='result')
                used=any(block.get('type')=='tool_use' for e in events if e.get('type')=='assistant' for block in e.get('message',{}).get('content',[]))
                usage=completed.get('usage',{})
                rows.append({'arm':name,'exit_code':result.returncode,'error':bool(completed.get('is_error')) or used,
                             'tool_calls':used,'skill_count':len(initialized.get('skills',[])),
                             'bundled_mcp_tools':sum('oci-readonly' in t for t in initialized.get('tools',[])),
                             'usage':{k:usage.get(k,0) for k in ('input_tokens','cache_creation_input_tokens','cache_read_input_tokens','output_tokens')}})
            except (OSError,ValueError,StopIteration,subprocess.TimeoutExpired):
                rows.append({'arm':name,'error':True})
    report={'date':datetime.now(timezone.utc).date().isoformat(),'host':version,'prompt':PROMPT,
            'method':'One A/B pair in an empty cwd, identical prompt and settings; input + cache creation + cache read tokens. CLI stream init records skill/tool counts. No tool calls; absent OCI config. Actual host framing, not chars/4. Strict empty MCP configuration isolates skills-only framing; bundled schemas are excluded.', 'runs':rows}
    if all(not r['error'] for r in rows):
        totals=[sum(r['usage'][k] for k in ('input_tokens','cache_creation_input_tokens','cache_read_input_tokens')) for r in rows]
        report.update(base_input_tokens=totals[0],plugin_input_tokens=totals[1],plugin_delta_tokens=totals[1]-totals[0])
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return int(any(r['error'] for r in rows))


if __name__=='__main__':
    raise SystemExit(main())
