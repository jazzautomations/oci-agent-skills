import asyncio
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tomllib

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def installed(tmp_path_factory):
    target = tmp_path_factory.mktemp("installer") / "plugin with spaces"
    subprocess.run(
        ["bash", str(ROOT / "installers/install.sh"), "--target", str(target)],
        check=True,
        capture_output=True,
    )
    return target


def test_installed_copies_and_refs(installed):
    assert not any(p.is_symlink() for p in installed.rglob("*"))
    assert not (installed / "runtime/.venv").exists()
    assert not (installed / "research").exists()
    for folder in (".agents", ".gemini", ".cursor", ".opencode"):
        skills = list((installed / folder / "skills").glob("*/SKILL.md"))
        assert len(skills) == 16
        import re

        for skill in skills:
            for target in re.findall(r"\]\(([^)]+)\)", skill.read_text()):
                if not target.startswith(("http:", "https:", "#")):
                    assert (skill.parent / target).exists(), (skill, target)
    assert (installed / "scripts/lib/oci_ro.sh").is_file()


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
                    assert len(tools) == 14
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
        ["bash", str(ROOT / "installers/install.sh"), "--target", str(target)],
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
