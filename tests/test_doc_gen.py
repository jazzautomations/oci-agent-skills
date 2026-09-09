"""Reader catalogs must reflect the shipped interface without using OCI credentials."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("doc_catalogs", ROOT / "scripts/doc-gen/catalogs.py")
catalogs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalogs)


def test_catalogs_match_shipped_interfaces(monkeypatch, tmp_path):
    monkeypatch.setenv("OCI_CONFIG_FILE", str(tmp_path / "missing"))
    for name, text in catalogs.render().items():
        assert (ROOT / name).read_text() == text, name


def test_catalog_preserves_scope_and_verification():
    skills = catalogs.load_skills()
    auth = skills["oci-cli-auth"]
    assert "auth-modes.md" in auth["shared"]  # Backtick links count too.
    assert auth["commands"] and all("--query" in command for command in auth["commands"])
    assert all("MUTATING" not in command for skill in skills.values() for command in skill["commands"])
    revised = {"sample": {**auth, "mode": "guarded-write", "verified": "shape-only"}}
    original = catalogs.DOMAINS
    try:
        catalogs.DOMAINS = {"Sample": ("sample",)}
        text = catalogs.skills_markdown(revised)
    finally:
        catalogs.DOMAINS = original
    assert "1 guarded-write" in text and "1 shape-only" in text
    assert auth["use"] in text and auth["exclude"] in text
