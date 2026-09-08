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
        "---\nname: oci-example\ndescription: Use when inspecting examples. Not for changes.\n---\n"
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
    p.write_text('```bash\noci compute instance terminate --instance-id "$ID"\n```')
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
