"""Generate offline read-option metadata from pinned Click definitions, never callbacks."""
import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path

from inventory import load_cli

ROOT = Path(__file__).resolve().parents[1]


def generate():
    import click
    from oci_cli.custom_types.cli_case_insensitive_choice import CliCaseInsensitiveChoice
    if version('oci-cli') != '3.91.0':
        raise ValueError('Use pinned OCI CLI 3.91.0')
    cli, errors = load_cli()
    if errors:
        raise ValueError('Incomplete CLI metadata')
    def options(command):
        aliases, choices = {}, {}
        for p in command.params:
            if not isinstance(p, click.Option):
                continue
            canonical = max(p.opts, key=len)
            aliases.update({flag: canonical for flag in p.opts if flag != canonical})
            if isinstance(p.type, click.Choice):
                choices[canonical] = {'values': list(p.type.choices),
                    'case_sensitive': p.type.case_sensitive and not isinstance(p.type, CliCaseInsensitiveChoice)}
        return {'aliases': aliases, 'choices': choices}
    reads = {r['path'] for r in map(json.loads, (ROOT / 'catalog/cli.jsonl').read_text().splitlines()) if r['read_only']}
    commands = {}
    def walk(command, path):
        if isinstance(command, click.Group):
            for name, child in command.commands.items():
                walk(child, [*path, name])
        elif ' '.join(path) in reads:
            commands[' '.join(path)] = options(command)
    walk(cli, [])
    if set(commands) != reads:
        raise ValueError('Read metadata does not match catalog')
    return {'oci_cli': version('oci-cli'),
            'catalog_sha256': hashlib.sha256((ROOT / 'catalog/cli.jsonl').read_bytes()).hexdigest(),
            'globals': options(cli), 'commands': commands}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    target = ROOT / 'catalog/read-contracts.json'
    data = json.dumps(generate(), sort_keys=True, indent=2) + '\n'
    if args.check:
        if not target.is_file() or target.read_text() != data:
            raise ValueError('Read-option contracts changed')
    else:
        target.write_text(data)
    print(json.dumps({'verified' if args.check else 'generated': True}))


if __name__ == '__main__':
    main()
