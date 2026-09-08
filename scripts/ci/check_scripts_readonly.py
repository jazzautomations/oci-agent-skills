#!/usr/bin/env python3
"""Static OCI-call policy and registry check; this is not proof against arbitrary Python."""
import ast
import shlex
import sys
from pathlib import Path
from common import ROOT, arguments, finding, finish

WRAPPERS = {'scripts/lib/oci_ro.py', 'scripts/lib/oci_ro.sh'}


def validate(path, root=ROOT):
    relative = path.relative_to(root).as_posix() if path.is_relative_to(root) else path.name
    if relative in WRAPPERS:
        return []
    text = path.read_text()
    result = []
    wrapped = 'oci_ro' in text
    skill_script = relative.startswith('skills/')
    if path.suffix == '.py':
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return [finding(path, 1, 'invalid_python')]
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                modules = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or '']
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
        for line, command in enumerate(text.splitlines(), 1):
            try:
                tokens = shlex.split(command, comments=True)
            except ValueError:
                continue
            if any(Path(token).name == 'oci' for token in tokens):
                result.append(finding(path, line, 'direct_oci'))
            if any(token in {'eval', 'bash -c', 'sh -c'} for token in tokens):
                result.append(finding(path, line, 'opaque_execution'))
    if skill_script and not wrapped:
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
