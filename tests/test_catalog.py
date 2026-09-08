import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from catalog import rows  # noqa: E402
from catalog_rules import annotate  # noqa: E402


def test_catalog_integrity():
    data = rows()
    assert len(data) == 9145
    assert len({r['path'] for r in data}) == len(data)
    assert data == sorted(data, key=lambda r: r['path'])
    assert rows(True) == [r for r in data if r['read_only']]
    for row in data:
        assert set(row['required']) <= set(row['flags'])
        assert row['cli_version'] == '3.91.0'
        assert all(row[k] == v for k, v in annotate(row['path']).items())
    index = json.loads((ROOT / 'catalog/index.json').read_text())
    assert not index['import_errors']
    assert sum(s['ops'] for s in index['services']) == len(data)
    for service in index['services']:
        selected = [r for r in data if r['path'].split()[0] == service['name']]
        assert service['ops'] == len(selected)
        assert service['read_only'] == sum(r['read_only'] for r in selected)


def test_examples_resolve():
    paths = {r['path'] for r in rows()}
    for example in json.loads((ROOT / 'catalog/examples.json').read_text())['examples']:
        assert (ROOT / 'skills' / example['skill'] / 'SKILL.md').is_file()
        argv = example['argv']
        end = next((i for i, v in enumerate(argv) if v.startswith('-')), len(argv))
        assert ' '.join(argv[:end]) in paths


def test_query_budget_and_discovery():
    for query in [('find', 'list instances'), ('help', 'compute instance list'),
                  ('severity', 'compute instance terminate'), ('service', 'compute')]:
        result = subprocess.check_output([sys.executable, str(ROOT / 'scripts/catalog.py'), *query])
        assert len(result) <= 400
        assert result.strip() and b'No matching' not in result


def test_generated_scripts_and_fragments():
    from inventory_artifacts import artifacts
    first = artifacts(scripts=True, examples=True)
    assert first == artifacts(scripts=True, examples=True)
    for name, content in first.items():
        assert (ROOT / 'catalog' / name).read_text() == content


def test_duplicate_fragment_rejected(tmp_path):
    import pytest
    from inventory_artifacts import artifacts
    (tmp_path / 'catalog/fragments').mkdir(parents=True)
    (tmp_path / 'catalog/cli-meta.json').write_text('{"scope":"fixture"}')
    row = {'id': 'same', 'skill': 'oci-example', 'argv': ['iam', 'region', 'list']}
    (tmp_path / 'catalog/fragments/oci-example.json').write_text(json.dumps([row, row]))
    with pytest.raises(ValueError, match='Duplicate'):
        artifacts(examples=True, root=tmp_path)
