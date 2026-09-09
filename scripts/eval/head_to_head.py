#!/usr/bin/env python3
"""Four-arm static comparison. Never launches competitor tools or model sessions."""
import argparse
import ast
import hashlib
import json
import math
import random
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'scripts/eval'), str(ROOT / 'scripts'), str(ROOT / 'scripts/ci')]
import yaml
import run as own
from graders import select, negative
from guard_lib import inspect_command
import lint_fences


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def snapshots():
    directory = ROOT / 'evals/arms'
    directory.mkdir(exist_ok=True)
    external = ROOT / 'research/refs/adibirzu_oci-skills'
    b = own.candidates(external)
    for candidate in b:
        p = Path(candidate.pop('path'))
        candidate['documents'] = []
        linked = {(p.parent / ref).resolve() for ref in re.findall(r'(?:\.\./)*references/[A-Za-z0-9_.-]+\.md', p.read_text())}
        for source in sorted({p, *list((p.parent / 'references').glob('*.md')), *[ref for ref in linked if ref.is_file()]}):
            candidate['documents'].append({'source': str(source.relative_to(external)), 'text': source.read_text()})
    router = ast.parse((external / 'hooks/inject_oci_router.py').read_text())
    context = next(ast.literal_eval(n.value) for n in router.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'ROUTER_CONTEXT' for t in n.targets))
    dump(directory / 'b.json', {'source': 'research/refs/adibirzu_oci-skills', 'candidates': b, 'router_context_characters': len(context), 'source_sha256': hashlib.sha256(json.dumps(b,sort_keys=True).encode()).hexdigest()})
    shutil.copyfile(external / 'LICENSE', directory / 'LICENSE-adibirzu.txt')
    oracle = ROOT / 'research/refs/oracle_mcp/src'
    c = []
    for service in ['oci-api', 'oci-cloud']:
        source = oracle / (service + '-mcp-server') / 'oracle' / (service.replace('-','_') + '_mcp_server') / 'server.py'
        tree = ast.parse(source.read_text())
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            decorators = [d for d in node.decorator_list if ast.unparse(d).startswith('mcp.tool')]
            if not decorators:
                continue
            description = ast.get_docstring(node) or ''
            for decorator in decorators:
                if isinstance(decorator, ast.Call):
                    for kw in decorator.keywords:
                        if kw.arg == 'description':
                            description = ast.literal_eval(kw.value)
            c.append({'name': node.name, 'description': description, 'signature': ast.unparse(node.args), 'server': service})
    dump(directory / 'c.json', {'source': 'research/refs/oracle_mcp', 'candidates': c, 'scope': 'Static descriptions/signatures; no imported server code or live tool calls.'})
    shutil.copyfile(oracle / 'oci-api-mcp-server/LICENSE.txt', directory / 'LICENSE-oracle.txt')
    deny = (oracle / 'oci-api-mcp-server/oracle/oci_api_mcp_server/denylist').read_text()
    (directory / 'oracle-denylist.txt').write_text(deny)


B_TARGETS = {
 'oci-navigator': ['oci-administrator','oci-project'], 'oci-cli-auth':['oci-administrator','oci-iam-admin'],
 'oci-tenancy-governance':['oci-landing-zone','oci-iam-admin'], 'oci-iam-policy':['oci-iam-admin'],
 'oci-support-limits':['oci-administrator'], 'oci-compute':['oci-networking-compute'],
 'oci-networking':['oci-networking-compute'], 'oci-object-storage':['oci-storage'],
 'oci-block-file-storage':['oci-storage'], 'oci-bastion-access':['oci-bastion-access'],
 'oci-oke':['oci-oke-admin'], 'oci-devops-pipelines':['oci-developer-services'],
 'oci-serverless':['oci-events-functions'], 'oci-terraform':['oci-terraform-authoring','oci-resource-manager'],
 'oci-monitoring-alarms':['oci-observability-db','oci-administrator'], 'oci-logging-audit':['oci-log-analytics'],
 'oci-incident-triage':['oci-administrator'], 'oci-security-posture':['oci-security-compliance','oci-data-safe','oci-zpr-visibility'],
 'oci-vault-certificates':['oci-security-compliance'], 'oci-cost-analysis':['oci-cost'], 'oci-free-tier':['oci-cost'],
 'oracle-autonomous-db':['oci-autonomous-db'], 'oracle-db-fleet':['oci-database-cloud','oci-dbm-opsi'],
 'oracle-db-vector-ai':['oci-application-engineering'], 'oracle-db-sql-access':['oci-application-engineering','oci-database-cloud'],
 'oracle-apex':['oci-application-engineering'], 'oci-generative-ai':['oci-data-platform','oci-application-engineering'],
 'oci-ai-services':['oci-data-platform'], 'oci-data-platform':['oci-data-platform'],
 'oci-sdk-patterns':['oci-developer-services','oci-application-engineering'], 'oci-dr-backup':['oci-disaster-recovery'],
 'oci-migration-patching':['oci-os-management','oci-database-cloud'], 'oracle-enterprise-apps':['oci-application-engineering','oci-product-development']}


def route_rows(rows, choices, arm):
    remap = own.read('remap.json')
    result = []
    for row in rows:
        selected = select(row['prompt'], choices)
        expected = remap.get(row['expected_skill'], row['expected_skill'])
        if arm == 'c':
            # This measures discovery-interface choice only, not the eventual operation.
            targets = ['get_oci_command_help'] if re.search(r'\bcli\b|\bcommand\b',row['prompt'],re.I) else ['find_oci_api','list_oci_clients','list_client_operations','describe_oci_operation']
        elif arm == 'b':
            targets = B_TARGETS.get(expected, [])
        else:
            targets = [expected]
        result.append({'id':row['id'], 'selected':selected, 'accepted_targets':targets, 'correct':selected is not None and selected in targets})
    return result


def b_fences(snapshot):
    import tempfile
    results = []
    seen = set()
    with tempfile.TemporaryDirectory(prefix='oci-eval-fences-') as folder:
        for candidate in snapshot['candidates']:
            for index, doc in enumerate(candidate['documents']):
                if doc['source'] in seen:
                    continue
                seen.add(doc['source'])
                text = re.sub(r'(?m)^(\s*)oci_cli ', r'\1oci ', doc['text'])
                path = Path(folder) / (str(index) + '.md')
                path.write_text(text)
                findings = {f['line']: f['code'] for f in lint_fences.validate(path)}
                for line, _ in lint_fences.commands(text):
                    results.append({'source':doc['source'], 'line':line, 'valid':line not in findings, 'finding':findings.get(line)})
    return results


def run():
    b = own.read('arms/b.json'); c = own.read('arms/c.json')
    choices = {'a':own.candidates(), 'b':b['candidates'], 'c':c['candidates'], 'd':[]}
    order = list(choices); random.Random(42).shuffle(order)
    report = {'mode':'offline-static-proxy', 'seed':42, 'run_order':order, 'model':None, 'temperature':None, 'runs':1, 'arms':{}}
    own_report = own.run()
    deny = [line for line in (ROOT / 'evals/arms/oracle-denylist.txt').read_text().splitlines() if line and not line.startswith('#')]
    for arm in order:
        routing = route_rows(own.read('routing.json'), choices[arm], arm)
        negatives = negative(own.read('negatives.json'), choices[arm])
        tasks = route_rows(own.read('tasks.json'), choices[arm], arm)
        fences = own_report['commands'] if arm == 'a' else b_fences(b) if arm == 'b' else []
        replay = []
        for fixture in own.read('guard-replay.json'):
            if arm == 'a':
                decision = inspect_command(fixture['command'])
            elif arm == 'c':
                command = fixture['command'].removeprefix('oci ').split(' --')[0]
                decision = ('deny' if any(command == item or command.startswith(item+' ') for item in deny) else 'allow') if fixture['command'].startswith('oci ') else 'outside_tool_surface'
            else:
                decision = 'unprotected'
            replay.extend({'id':fixture['id'], 'run':i+1, 'decision':decision} for i in range(5))
        description_chars = sum(len(item['description']) for item in choices[arm])
        tokens = math.ceil(description_chars / 4)
        if arm == 'a':
            import asyncio
            sys.path.insert(0,str(ROOT / 'runtime'))
            from oci_readonly.server import mcp
            schema = json.dumps([t.model_dump(exclude_none=True) for t in asyncio.run(mcp.list_tools())], separators=(',',':'))
            tokens += math.ceil(len(schema)/4)
        report['arms'][arm] = {'routing_accuracy':sum(r['correct'] for r in routing)/len(routing),
            'false_positive_rate':sum(r['selected'] is not None for r in negatives)/len(negatives),
            'command_validity':sum(f['valid'] for f in fences)/len(fences) if fences else None,
            'fence_count':len(fences), 'guard_unconfirmed_exposure':sum(r['decision'] in ['allow','unprotected'] for r in replay),
            'guard_replay_count':len(replay), 'always_resident_tokens_estimate':tokens,
            'token_basis':'descriptions + serialized MCP schemas' if arm=='a' else 'descriptions only; tool schemas omitted lower bound' if arm=='c' else 'descriptions only',
            'router_injection_tokens_estimate': math.ceil(b['router_context_characters']/4) if arm=='b' else 0,
            'routing':routing, 'negatives':negatives,'tasks':tasks,'commands':fences,'guard_replay':replay}
    report['per_case_no_plugin_delta'] = [{'id':a['id'], 'retrieval_delta':int(a['correct'])-int(d['correct']), 'behavioral_delta':None} for group in ('routing','tasks') for a,d in zip(report['arms']['a'][group], report['arms']['d'][group])]
    return report


def markdown(report):
    text = '''# Four-arm offline comparison — 2026-09-09

Reproduce: `uv run --frozen --project runtime python scripts/eval/head_to_head.py --json evals/results/head-to-head.json --markdown docs/head-to-head.md`.
Refresh competitor snapshots from the named research checkouts with the same command plus `--refresh-snapshots`. The shipped snapshots carry the original MIT/UPL notices. No competitor server is launched.

All arms receive identical unedited prompts, the same description matcher, one deterministic run, no model or temperature, and no placeholder substitution or tenancy access. Arm order is seeded and shuffled. Arm b retains every shipped skill, including its router. A domain crosswalk maps equivalent b routes; it is scoring-only and never enters selection. Arm c uses both servers' tool descriptions and scores discovery-interface choice; it does not prove correct API operation selection. That asymmetry is not averaged with skill routing. Bare has no descriptions, so it abstains: it is not a measurement of a bare model's knowledge.

| Arm | Routing proxy | Negative firing rate | Authored fence validity | Unconfirmed guard exposure | Resident token estimate |
|---|---:|---:|---:|---:|---:|
'''
    names = {'a':'This pack','b':'adibirzu skills','c':'Oracle API + Cloud tools','d':'Bare descriptor baseline'}
    for arm in 'abcd':
        r=report['arms'][arm]
        valid='unmeasured (no authored fences)' if r['command_validity'] is None else f"{r['command_validity']:.1%} / {r['fence_count']}"
        text += f"| {names[arm]} | {r['routing_accuracy']:.1%} | {r['false_positive_rate']:.1%} | {valid} | {r['guard_unconfirmed_exposure']}/{r['guard_replay_count']} | {r['always_resident_tokens_estimate']} |\n"
    text += f"\nOrder: {', '.join(report['run_order'])}; seed {report['seed']}. Token estimates use characters / 4 rounded up. Arm a includes actual serialized MCP schemas; arm c is a **description-only lower bound**, not a full schema floor. Arm b additionally ships a UserPromptSubmit router injection of approximately {report['arms']['b']['router_injection_tokens_estimate']} tokens per turn; the static matcher does not simulate it. Research's statement that b has no hook means no mutation guard: its prompt hook exists.\n"
    text += '''
Guard exposure counts inert mutation fixtures that an available guard would allow or leave unprotected, five replays per case. Arm c measures only its CLI denylist; Terraform is outside its tool surface, and SDK invocation protection remains unmeasured. These are not executed mutations or agent confirmation behavior. The same authored-fence linter grades skill bodies and their directly referenced documents in both skill arms. The known forwarding wrapper spelling oci_cli is normalized to oci for syntax lint only; arbitrary wrapper chains are not interpreted. No authored output exists for c/d, so their command-validity metric is unmeasured, not fabricated as zero or perfect.

The raw JSON contains every routing, negative, task-retrieval and guard-replay result, plus per-case a-minus-d retrieval deltas for routing and tasks. A nonpositive delta is an offline review candidate; it cannot justify deleting a skill without a model-backed baseline. Behavioral task scores, generated-command validity, leakage and live injection remain unmeasured. V19 is red; V27 and the original live V28 cannot be established by this offline comparison. Owners: evaluation/routing maintainers for V19 and V28; Claude early-access provider plus evaluation maintainers for V27. The requested four-arm offline comparison is complete.
'''
    return text


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh-snapshots',action='store_true')
    parser.add_argument('--json',type=Path,default=ROOT/'evals/results/head-to-head.json')
    parser.add_argument('--markdown',type=Path,default=ROOT/'docs/head-to-head.md')
    args=parser.parse_args()
    if args.refresh_snapshots: snapshots()
    report=run(); dump(args.json,report); args.markdown.write_text(markdown(report))
    print(json.dumps({arm:{k:v for k,v in row.items() if k not in ['routing','negatives','tasks','commands','guard_replay']} for arm,row in report['arms'].items()},indent=2))


if __name__=='__main__': main()
