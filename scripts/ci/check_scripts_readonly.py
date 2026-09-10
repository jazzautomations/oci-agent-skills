#!/usr/bin/env python3
"""Static OCI-call policy and registry check; this is not proof against arbitrary Python."""
import ast
import shlex
import re
import sys
from pathlib import Path
from common import ROOT, arguments, finding, finish

OFFLINE = {'skills/oci-migration-assess/scripts/inventory_normalize.py', 'skills/oci-migration-landing-zone/scripts/emit_tfvars.py', 'skills/oci-networking/scripts/merge_rules.py', 'skills/oci-terraform/scripts/plan_summary.py', 'skills/oci-generative-ai/scripts/chat_min.py'}
PUBLIC_GET = {'skills/oci-migration-map/scripts/map_and_price.py', 'skills/oci-sdk-patterns/scripts/fetch_spec.py', 'skills/oci-cost-analysis/scripts/price.sh', 'skills/oci-cost-analysis/scripts/price.py'}


def calls_wrapper(tree):
    aliases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for item in node.names:
                aliases[item.asname or item.name] = (node.module or '') + '.' + item.name
        elif isinstance(node, ast.Import):
            for item in node.names:
                aliases[item.asname or item.name] = item.name
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = ast.unparse(node.func)
            first, _, tail = name.partition('.')
            resolved = aliases.get(first, first) + ('.' + tail if tail else '')
            if resolved in {'lib.oci_ro.run', 'lib.oci_ro.run_process'}:
                return True
    return False


WRAPPERS = {'scripts/lib/oci_ro.py', 'scripts/lib/oci_ro.sh'}


def validate(path, root=ROOT):
    relative = path.relative_to(root).as_posix() if path.is_relative_to(root) else path.name
    if relative in WRAPPERS:
        return []
    text = path.read_text()
    result = []
    wrapped = False
    skill_script = relative.startswith('skills/')
    if path.suffix == '.py':
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return [finding(path, 1, 'invalid_python')]
        wrapped = calls_wrapper(tree)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                modules = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or '']
                if relative in OFFLINE and any(m.split('.')[0] in {'oci','socket','requests','httpx','urllib','subprocess','importlib','builtins'} for m in modules):
                    result.append(finding(path, node.lineno, 'offline_network_or_executor'))
                if skill_script and any(m == 'oci' or m.startswith('oci.') for m in modules):
                    result.append(finding(path, node.lineno, 'direct_sdk'))
            if not isinstance(node, ast.Call):
                continue
            name = ast.unparse(node.func)
            if name in {'eval', 'exec', 'os.system', 'os.popen'}:
                result.append(finding(path, node.lineno, 'opaque_execution'))
            if name.startswith('subprocess.') and node.args:
                arg = node.args[0]
                values = [v.value for v in ast.walk(arg) if isinstance(v, ast.Constant) and isinstance(v.value, str)]
                if any(v == 'oci' or v.startswith('oci ') for v in values):
                    result.append(finding(path, node.lineno, 'direct_oci'))
                if skill_script:
                    result.append(finding(path, node.lineno, 'skill_subprocess_outside_wrapper'))
    elif path.suffix == '.sh':
        # Shell entrypoints either invoke the sourced function, delegate to a validated
        # sibling, or contain a Python heredoc with a resolved wrapper call.
        shell = '\n'.join(line for line in text.splitlines() if not line.lstrip().startswith('#'))
        wrapped = bool(re.search(r'(?:^|[;{]\s*|\s)oci_ro\s+(?:--|[a-z])', shell) and re.search(r'(?:^|\n)\s*(?:source|\.)\s+.*oci_ro\.sh', shell))
        for child in re.findall(r'exec python3 "\$DIR/([a-z_]+\.py)" "\$@"', shell):
            target = path.parent / child
            if target.is_file() and not validate(target, root):
                wrapped = True
        for delimiter, body in re.findall(r"<<'([A-Z]+)'\n(.*?)\n\1", text, re.S):
            try:
                if calls_wrapper(ast.parse(body)):
                    wrapped = True
            except SyntaxError:
                pass
        for line, command in enumerate(text.splitlines(), 1):
            try:
                tokens = shlex.split(command, comments=True)
            except ValueError:
                continue
            if any(Path(token).name == 'oci' for token in tokens):
                result.append(finding(path, line, 'direct_oci'))
            if any(token in {'eval', 'bash -c', 'sh -c'} for token in tokens):
                result.append(finding(path, line, 'opaque_execution'))
    if skill_script and not wrapped and relative not in OFFLINE | PUBLIC_GET:
        result.append(finding(path, 1, 'missing_wrapper'))
    return result


def main():
    args = arguments(__doc__)
    selected = []
    for root in args.paths or [ROOT / 'scripts', ROOT / 'skills']:
        if root.is_file():
            selected.append(root)
        else:
            selected.extend(p for p in root.rglob('*') if p.suffix in {'.sh', '.py'} and '__pycache__' not in p.parts and ('scripts' in p.parts))
    findings = [f for p in selected for f in validate(p)]
    if not args.paths:
        sys.path.insert(0, str(ROOT / 'scripts'))
        from inventory_artifacts import artifacts
        for name, content in artifacts(scripts=True).items():
            path = ROOT / 'catalog' / name
            if not path.exists() or path.read_text() != content:
                findings.append(finding(path, 1, 'script_registry_drift'))
    return finish('scripts_readonly', findings, args, len(selected))


if __name__ == '__main__':
    raise SystemExit(main())
