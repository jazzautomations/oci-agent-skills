"""Template verification must work in a clean checkout without private research."""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_template_check_without_research_detects_drift(tmp_path):
    for name in ("scripts/ci/check_template.py", "scripts/ci/common.py",
                 "scripts/ci/template-source.json", "skills/_TEMPLATE/SKILL.md.template"):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    command = [sys.executable, str(tmp_path / "scripts/ci/check_template.py")]
    assert not (tmp_path / "research").exists()
    assert subprocess.run(command, capture_output=True).returncode == 0
    template = tmp_path / "skills/_TEMPLATE/SKILL.md.template"
    template.write_text(template.read_text() + "unreviewed change\n")
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 1 and "differs" in result.stderr


def test_template_write_requires_an_explicit_plan():
    result = subprocess.run([sys.executable, str(ROOT / "scripts/ci/check_template.py"),
                             "--write"], capture_output=True, text=True)
    assert result.returncode == 2 and "requires an explicit --plan" in result.stderr
