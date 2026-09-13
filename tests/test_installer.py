import asyncio
import errno
import importlib.util
import json
import os
import re
from pathlib import Path
import subprocess
import tomllib

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('number,message', [
    (errno.ENOSPC, 'Not enough disk space to copy the installation'),
    (errno.EDQUOT, 'Storage quota exceeded while copying the installation'),
    (errno.EACCES, 'Permission denied while copying the installation'),
    (errno.EPERM, 'Permission denied while copying the installation'),
    (errno.EIO, 'Unable to copy the installation'),
])
def test_installation_io_errors_are_actionable_without_private_paths(
        monkeypatch, capsys, number, message):
    spec = importlib.util.spec_from_file_location('installer', ROOT / 'installers/install.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    def fail(*args, **kwargs):
        raise OSError(number, 'private diagnostic detail', '/private/account/file')

    monkeypatch.setattr(module, 'install', fail)
    monkeypatch.setattr('sys.argv', ['install.py', '--target', '/unused'])
    assert module.main() == 1
    captured = capsys.readouterr()
    assert json.loads(captured.out) == {'ok': False, 'error': message}
    assert not captured.err


@pytest.fixture(scope="module")
def installed(tmp_path_factory):
    target = tmp_path_factory.mktemp("installer") / "plugin with spaces"
    subprocess.run(
        ["bash", str(ROOT / "installers/install.sh"), "--target", str(target), "--i-accept-unguarded"],
        check=True,
        capture_output=True,
    )
    return target


def test_installed_copies_and_refs(installed):
    assert not any(p.is_symlink() for p in installed.rglob("*"))
    assert not (installed / "runtime/.venv").exists()
    assert not (installed / "research").exists()
    assert not list(installed.rglob("CODEX-STATUS.md"))
    assert not (installed / "docs/build-log").exists()
    assert not list(installed.rglob(".handoff-*"))
    for folder in (".agents", ".gemini", ".cursor", ".opencode"):
        skills = list((installed / folder / "skills").glob("*/SKILL.md"))
        assert len(skills) == len(list((ROOT / 'skills').glob('*/SKILL.md')))
        import re

        for skill in skills:
            for target in re.findall(r"\]\(([^)]+)\)", skill.read_text()):
                if not target.startswith(("http:", "https:", "#")):
                    assert (skill.parent / target).exists(), (skill, target)
    assert (installed / "scripts/lib/oci_ro.sh").is_file()


def test_installed_reader_documentation_links(installed):
    from urllib.parse import unquote, urlsplit

    documents = [installed / "README.md", installed / "SECURITY.md",
                 installed / "CHANGELOG.md", *(installed / "docs").rglob("*.md")]
    for document in documents:
        text = re.sub(r"(?ms)^(`{3,}|~{3,}).*?^\1[^\n]*", "", document.read_text())
        for target in re.findall(r"\]\(([^\s)]+)\)", text):
            parsed = urlsplit(unquote(target))
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            assert (document.parent / parsed.path).exists(), (document, target)
    assert "https://github.com/jazzautomations/oci-agent-skills/blob/main/docs/build-log/README.md" in (installed / "README.md").read_text()


@pytest.mark.parametrize("host", ["codex", "gemini", "cursor", "opencode"])
def test_installed_host_launcher(installed, host, tmp_path):
    if host == "codex":
        spec = tomllib.loads((installed / ".codex/config.toml").read_text())[
            "mcp_servers"
        ]["oci-readonly"]
    elif host in ("gemini", "cursor"):
        file = ".gemini/settings.json" if host == "gemini" else ".cursor/mcp.json"
        spec = json.loads((installed / file).read_text())["mcpServers"]["oci-readonly"]
    else:
        argv = json.loads((installed / "opencode.json").read_text())["mcp"]["servers"][
            "oci-readonly"
        ]["command"]
        spec = {"command": argv[0], "args": argv[1:]}

    async def check():
        env = dict(os.environ, OCI_CONFIG_FILE=str(tmp_path / "missing"))
        parameters = StdioServerParameters(
            command=spec["command"], args=spec["args"], env=env, cwd=tmp_path
        )
        async with asyncio.timeout(60):
            async with stdio_client(parameters) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = (await session.list_tools()).tools
                    assert len(tools) == 15
                    assert all(
                        t.annotations.readOnlyHint and not t.annotations.destructiveHint
                        for t in tools
                    )

    asyncio.run(check())


def test_installer_preserves_existing_target(tmp_path):
    target = tmp_path / "existing"
    target.mkdir()
    marker = target / "user-data"
    marker.write_text("preserve")
    result = subprocess.run(
        ["bash", str(ROOT / "installers/install.sh"), "--target", str(target), "--i-accept-unguarded"],
        capture_output=True,
    )
    assert result.returncode == 1
    assert marker.read_text() == "preserve"
    assert list(target.iterdir()) == [marker]


def test_copy_refuses_symlink(tmp_path):
    # Mock a symlink predicate instead of creating a link in the workspace.
    spec = importlib.util.spec_from_file_location(
        "installer", ROOT / "installers/install.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    from unittest.mock import Mock

    source = Mock()
    source.is_symlink.return_value = True
    with pytest.raises(ValueError):
        module.copy_payload(source, tmp_path / "destination")


@pytest.mark.parametrize('host', ['codex', 'gemini', 'cursor', 'opencode', 'all'])
def test_unguarded_install_gate(tmp_path, host):
    target = tmp_path / host
    result = subprocess.run(['bash', str(ROOT / 'installers/install.sh'), '--target', str(target), '--host', host], capture_output=True, text=True)
    assert result.returncode != 0 and 'UNGUARDED' in result.stdout
    assert not target.exists()


def test_copy_shared_and_claude_install(tmp_path):
    target = tmp_path / 'claude'
    result = subprocess.run(['bash', str(ROOT / 'installers/install.sh'), '--target', str(target), '--host', 'claude', '--copy-shared'], check=True, capture_output=True, text=True)
    report = json.loads(result.stdout)
    assert report['shared_copied']
    assert report['runtime_setup'] == ['uv','sync','--frozen','--project',str(target/'runtime')]
    assert not any(p.is_symlink() for p in target.rglob('*'))
    assert not (target / 'skills/_TEMPLATE').exists()
    shared = list((ROOT / 'references').glob('*'))
    for skill in (target / 'skills').iterdir():
        for path in shared:
            if path.is_file():
                assert (skill / 'references' / ('shared-' + path.name)).is_file()


def test_materialize_shared_rewrites_route_and_json_link(tmp_path):
    spec = importlib.util.spec_from_file_location('installer', ROOT / 'installers/install.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    refs = tmp_path / 'references'
    refs.mkdir()
    (refs / 'errors.md').write_text('[corpus](error-corpus.json)')
    (refs / 'error-corpus.json').write_text('{}')
    skill = tmp_path / 'skills/oci-fixture'
    skill.mkdir(parents=True)
    (skill / 'SKILL.md').write_text('## Route\n| error | `../../references/errors.md` | load when errors |\n[corpus](../../references/error-corpus.json)')
    module.materialize_shared(tmp_path)
    assert '../../references/' not in (skill / 'SKILL.md').read_text()
    assert '[corpus](shared-error-corpus.json)' in (skill / 'references/shared-errors.md').read_text()
