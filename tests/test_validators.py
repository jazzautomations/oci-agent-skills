import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/ci"))


def module(name):
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "scripts/ci" / (name + ".py")
    )
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def test_frontmatter_routes_and_length(tmp_path):
    p = tmp_path / "oci-example" / "SKILL.md"
    p.parent.mkdir()
    p.write_text(
        "---\nname: oci-example\ndescription: \"Use when: inspecting examples. Not for: changes.\"\nmetadata:\n  verified: shape-only\n---\n"
    )
    validator = module("check_frontmatter")
    assert not validator.validate(p)
    p.write_text(p.read_text().replace("Not for", "Avoid"))
    assert validator.validate(p)[0]["code"] == "description_routing"


def test_refs_missing_and_cross_docs(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text(
        "[bad](missing.md)\n[bad](../../docs/operations.md)\n[web](https://example.invalid)"
    )
    codes = [x["code"] for x in module("check_refs").validate(p)]
    assert codes.count("missing_reference") == 2
    assert "cross_docs_reference" in codes


def test_fences_validate_leaf_required_and_bounds(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text("""```bash
oci compute instance --help
oci compute instance list
oci compute instance list --compartment-id "$C"
oci compute instance list --compartment-id "$C" \\
  --limit 2
oci compute instance terminate --help
```""")
    found = module("lint_fences").validate(p)
    assert [f["code"] for f in found] == [
        "unknown_leaf",
        "missing_required_flags",
        "unbounded_list",
    ]


def test_live_help_never_runs_example(tmp_path, monkeypatch):
    p = tmp_path / "SKILL.md"
    p.write_text('```bash\n# MUTATING — not run; [shape-verified]\n# rollback: NONE — irreversible\noci compute instance terminate --instance-id "$ID"\n```')
    lint = module("lint_fences")

    def fake(argv, **kwargs):
        from types import SimpleNamespace

        assert argv == ["compute", "instance", "terminate", "--help"]
        return SimpleNamespace(returncode=0, stdout="--instance-id")

    monkeypatch.setattr(lint, "run", fake)
    assert not lint.validate(p, True)


def test_secrets_and_symlinks(tmp_path):
    p = tmp_path / "data.txt"
    p.write_text("ocid1.tenancy.oc1.." + "a" * 32)
    validator = module("check_no_secrets")
    assert validator.validate(p)[0]["code"] == "real_ocid"
    p.write_text("ocid1.tenancy.oc1..example")
    assert not validator.validate(p)


def test_new_validators_reject_real_violations(tmp_path):
    p = tmp_path / 'oci-example' / 'SKILL.md'
    p.parent.mkdir()
    p.write_text('---\nname: oci-example\ndescription: "Use when: examples. Not for: changes."\nmetadata:\n  verified: partial\npaths: ["*.tf"]\n---\n')
    assert not module('check_portable').validate(p)
    p.write_text(p.read_text().replace('partial', 'guessed'))
    assert module('check_frontmatter').validate(p)[0]['code'] == 'metadata_verified'
    p.write_text('```bash\noci compute instance terminate --instance-id example\n```')
    assert module('lint_fences').validate(p)[0]['code'] == 'mutation_marker'
    p.write_text('```bash\n# MUTATING [shape-verified]\noci compute instance terminate --instance-id example\n```')
    assert module('lint_fences').validate(p)[0]['code'] == 'mutation_rollback'
    p.write_text('x' * 6001)
    assert module('check_budget').validate(p)[0]['code'] == 'body_budget_estimate'
    script = tmp_path / 'bad.py'
    script.write_text('import subprocess\nsubprocess.run(["oci", "compute", "instance", "terminate"])\n')
    assert module('check_scripts_readonly').validate(script)[0]['code'] == 'direct_oci'
    assert module('check_licenses').validate(tmp_path)[0]['code'] == 'root_apache_license'
    assert module('check_links').urls('[x](https://docs.oracle.com/example.htm)') == {'https://docs.oracle.com/example.htm'}


def test_refs_non_markdown_exempt_and_route_names(tmp_path):
    refs = tmp_path / 'references'
    refs.mkdir()
    data = refs / 'error-corpus.json'
    data.write_text('{}')
    ref = refs / 'errors.md'
    ref.write_text('Errors\n')
    skill = tmp_path / 'SKILL.md'
    skill.write_text('## Route\n')
    validator = module('check_refs')
    assert not validator.validate(data)
    assert validator.validate(skill)[0]['code'] == 'unnamed_reference'
    skill.write_text('## Route\n| error | `references/errors.md` | Load when errors occur |\n')
    assert not validator.validate(skill)
