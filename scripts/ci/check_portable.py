#!/usr/bin/env python3
"""Validate the portable six-key metadata projection; report CC-only keys removed."""
import yaml
from common import arguments, files, finding, finish
from check_frontmatter import validate_data

PORTABLE = {'name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools'}


def project(data):
    return {key: value for key, value in data.items() if key in PORTABLE}


def validate(path):
    if path.name != 'SKILL.md' or path.parent.name == '_TEMPLATE':
        return []
    try:
        text = path.read_text()
        data = yaml.safe_load(text.split('---', 2)[1])
        if not isinstance(data, dict):
            raise ValueError()
        portable = yaml.safe_load(yaml.safe_dump(project(data)))
        return validate_data(path, portable)
    except (ValueError, IndexError, yaml.YAMLError):
        return [finding(path, 1, 'invalid_yaml')]


if __name__ == '__main__':
    args = arguments(__doc__)
    selected = [p for p in files(args.paths) if p.name == 'SKILL.md']
    raise SystemExit(finish('portable', [f for p in selected for f in validate(p)], args, len(selected)))
