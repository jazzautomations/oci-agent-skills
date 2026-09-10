"""Exercise the actual bundled host launch configurations over MCP stdio."""

import asyncio
import json
import os
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]


def test_live_smoke_requires_a_resolvable_region(monkeypatch, tmp_path):
    from oci_readonly import smoke

    monkeypatch.delenv("OCI_REGION", raising=False)
    monkeypatch.setenv("OCI_CONFIG_FILE", str(tmp_path / "missing"))
    monkeypatch.setattr("sys.argv", ["oci-readonly-smoke", "--live"])
    with pytest.raises(SystemExit) as caught:
        smoke.main()
    assert caught.value.code == 2


@pytest.mark.parametrize("host", ["claude", "codex"])
def test_host_config_starts_from_resolved_plugin_root(host, tmp_path):
    if host == "claude":
        config = json.loads((ROOT / ".mcp.json").read_text())["mcpServers"]["oci-readonly"]
        # Claude's documented plugin expansion; launch from unrelated workspace.
        args = [arg.replace("${CLAUDE_PLUGIN_ROOT}", str(ROOT)) for arg in config["args"]]
        cwd = tmp_path
    else:
        manifest = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
        config = manifest["mcpServers"]["oci-readonly"]
        # Codex 0.153.4 anchors a relative plugin MCP cwd to the installed root.
        args = config["args"]
        cwd = ROOT / config["cwd"]

    async def check():
        env = dict(os.environ)
        # A tools/list smoke must not require valid account credentials.
        env["OCI_CONFIG_FILE"] = str(tmp_path / "no-credentials")
        parameters = StdioServerParameters(command=config["command"], args=args, env=env, cwd=cwd)
        async with asyncio.timeout(30):
            async with stdio_client(parameters) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = (await session.list_tools()).tools
                    assert len(tools) == 15
                    assert all(t.annotations.readOnlyHint for t in tools)
                    assert all(not t.annotations.destructiveHint for t in tools)

    asyncio.run(check())


def test_w08b_manifest_shape():
    plugin = json.loads((ROOT / '.claude-plugin/plugin.json').read_text())
    market = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
    assert plugin['mcpServers'] == './.mcp.json'
    assert (ROOT / plugin['mcpServers']).is_file()
    assert plugin['version'] == '0.2.1' and 'skills' not in plugin
    assert {entry['name'] for entry in market['plugins']} == {'oci-agent-skills', 'oci-agent-skills-db', 'oci-agent-skills-devops'}
    for entry in market['plugins']:
        assert len(entry['skills']) == {'oci-agent-skills': len(list((ROOT / 'skills').glob('*/SKILL.md'))), 'oci-agent-skills-db': 8, 'oci-agent-skills-devops': 9}[entry['name']]
        assert all((ROOT / path / 'SKILL.md').is_file() for path in entry['skills'])
        assert entry['hooks'] == './hooks/hooks.json'
        assert (ROOT / entry['hooks']).is_file()
        assert 'not affiliated with' in entry['description']
    codex = json.loads((ROOT / '.codex-plugin/plugin.json').read_text())
    assert 'hooks' not in codex
    assert codex['mcpServers']['oci-readonly']['cwd'] == '.'


def test_smoke_profile_region(monkeypatch, tmp_path):
    from oci_readonly.smoke import profile_region
    config=tmp_path/'config'
    config.write_text('[DEFAULT]\nregion=us-ashburn-1\n[OTHER]\nregion=us-phoenix-1\n')
    monkeypatch.setenv('OCI_CONFIG_FILE',str(config))
    monkeypatch.setenv('OCI_CONFIG_PROFILE','OTHER')
    assert profile_region() == 'us-phoenix-1'
