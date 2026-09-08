#!/usr/bin/env python3
"""W08a manifest shape, optionally installed Claude strict validation without the stencil."""
import argparse
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path
from common import ROOT


def validate():
    plugin = json.loads((ROOT / '.claude-plugin/plugin.json').read_text())
    marketplace = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
    codex = json.loads((ROOT / '.codex-plugin/plugin.json').read_text())
    assert plugin['name'] == codex['name'] == 'oci-agent-skills'
    assert plugin['version'] == codex['version'] == '0.2.1'
    assert 'skills' not in plugin and 'hooks' not in codex
    assert len(marketplace['plugins']) == 3
    for entry in marketplace['plugins']:
        assert 'skills' not in entry
        assert entry['hooks'] == './hooks/hooks.json' and entry['source'] == './'
    assert codex['mcpServers']['oci-readonly']['cwd'] == '.'
    assert (ROOT / plugin['hooks']).is_file()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host-validation', action='store_true')
    args = parser.parse_args()
    validate()
    if args.host_validation:
        spec = importlib.util.spec_from_file_location('installer', ROOT / 'installers/install.py')
        installer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(installer)
        with tempfile.TemporaryDirectory(prefix='oci-manifest-check-') as directory:
            target = Path(directory) / 'oci-agent-skills'
            installer.install(target, host='claude')
            for path in (target, target / '.claude-plugin/marketplace.json'):
                result = subprocess.run(['claude', 'plugin', 'validate', str(path), '--strict', '--json'], capture_output=True, text=True, check=True)
                report = json.loads(result.stdout)
                assert report['success']
    print('W08a manifests valid' + ('; copied plugin passes Claude strict validation.' if args.host_validation else '.'))
