#!/usr/bin/env python3
"""Validate skill metadata: directory name, bounded description and explicit routing."""
import re
import yaml
from common import arguments, files, finding, finish


def validate(path):
    if path.name != 'SKILL.md':
        return []
    text = path.read_text()
    if not text.startswith('---\n'):
        return [finding(path, 1, 'missing_frontmatter')]
    parts = text.split('---', 2)
    if len(parts) < 3:
        return [finding(path, 1, 'unclosed_frontmatter')]
    try:
        data = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        data = None
    if not isinstance(data, dict):
        return [finding(path, 1, 'invalid_yaml')]
    result = []
    name = data.get('name', '')
    if not isinstance(name, str) or not re.fullmatch(r'(oci|oracle)-[a-z0-9]+(?:-[a-z0-9]+)*', name):
        result.append(finding(path, 2, 'invalid_name'))
    if path.parent.name != '_TEMPLATE' and name != path.parent.name:
        result.append(finding(path, 2, 'name_directory_mismatch'))
    description = data.get('description')
    if not isinstance(description, str) or not 1 <= len(description) <= 400:
        result.append(finding(path, 3, 'description_length'))
    elif 'Use when' not in description or 'Not for' not in description:
        result.append(finding(path, 3, 'description_routing'))
    return result


def main():
    args = arguments(__doc__)
    selected = [p for p in files(args.paths) if p.name == 'SKILL.md']
    return finish('frontmatter', [f for p in selected for f in validate(p)], args, len(selected))


if __name__ == '__main__':
    raise SystemExit(main())
