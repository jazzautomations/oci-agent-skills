"""Deterministic script registry, guard policy and example-fragment generators."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def script_rows(root=ROOT):
    paths = set((root / 'scripts').rglob('*.py')) | set((root / 'scripts').rglob('*.sh'))
    paths |= set((root / 'skills').glob('*/scripts/*.py')) | set((root / 'skills').glob('*/scripts/*.sh'))
    result = []
    for path in sorted(paths):
        if '__pycache__' in path.parts or path.is_symlink():
            continue
        calls = []
        if path.suffix == '.py':
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and node.args and isinstance(node.args[0], (ast.List, ast.Tuple)):
                    values = [v.value for v in node.args[0].elts if isinstance(v, ast.Constant) and isinstance(v.value, str)]
                    if values and values[0] in {'oci', 'compute', 'iam', 'os', 'limits', 'search'}:
                        calls.append(values)
        result.append({'path': path.relative_to(root).as_posix(),
                       'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                       'mode': 'read-only', 'oci_calls': calls})
    return result


def artifacts(*, scripts=False, examples=False, root=ROOT):
    scope = json.loads((root / 'catalog/cli-meta.json').read_text())['scope']
    result = {}
    if scripts:
        registry = {'scope': scope, 'scripts': script_rows(root)}
        result['scripts.json'] = json.dumps(registry, indent=2) + '\n'
        guard = json.loads((root / 'scripts/guard_rules.json').read_text())
        guard['scope'] = scope
        guard['scripts_sha256'] = hashlib.sha256(result['scripts.json'].encode()).hexdigest()
        result['guard.json'] = json.dumps(guard, indent=2) + '\n'
    if examples:
        rows, ids = [], set()
        for path in sorted((root / 'catalog/fragments').glob('*.json')):
            fragment = json.loads(path.read_text())
            for row in fragment if isinstance(fragment, list) else fragment['examples']:
                if not isinstance(row, dict) or not {'id', 'skill', 'argv'} <= row.keys() or not isinstance(row['argv'], list) or not all(isinstance(v, str) for v in row['argv']):
                    raise ValueError('Invalid example row in ' + path.name)
                if row['id'] in ids:
                    raise ValueError('Duplicate example id: ' + row['id'])
                ids.add(row['id'])
                rows.append(row)
        result['examples.json'] = json.dumps({'scope': scope, 'description': 'Scoped read-only CLI argv templates. Validation does not imply deployed service coverage. Replace placeholders locally; never publish account values.', 'examples': sorted(rows, key=lambda row: row['id'])}, indent=2) + '\n'
    return result
