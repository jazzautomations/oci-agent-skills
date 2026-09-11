"""Offline OCI read-command checks. Never execute commands, callbacks or shell expansion."""
import argparse
import difflib
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
import shlex

from guard_lib import catalog_data, parse_oci, readonly_argv

ROOT = Path(__file__).resolve().parents[1]
SCOPE = 'Offline syntax only; query meaning, service callbacks, authorization and completeness are not certified.'


def shell_substitution(command):
    quote = None
    escaped = False
    for char in command:
        if escaped:
            escaped = False
            continue
        if char == '\\' and quote != "'":
            escaped = True
        elif char == quote:
            quote = None
        elif char in "'\"" and quote is None:
            quote = char
        elif char == '`' and quote != "'":
            return True
    return False


@lru_cache(maxsize=1)
def contracts():
    data = json.loads((ROOT / 'catalog/read-contracts.json').read_text())
    if data['catalog_sha256'] != hashlib.sha256((ROOT / 'catalog/cli.jsonl').read_bytes()).hexdigest():
        raise ValueError('Option metadata differs from catalog')
    return data


def describe(leaf):
    if not isinstance(leaf, str) or len(leaf) > 200:
        return {'ok': False, 'reason': 'invalid_leaf', 'scope': SCOPE}
    leaf = leaf.removeprefix('oci ').strip()
    row = catalog_data()[0].get(leaf)
    data = contracts()
    if leaf not in data['commands'] or not row or not row['read_only'] or leaf == 'raw-request':
        return {'ok': False, 'reason': 'unknown_or_nonread_leaf',
                'suggestions': difflib.get_close_matches(leaf, data['commands'], n=3), 'scope': SCOPE}
    return {'ok': True, 'leaf': leaf, 'required': row['required'],
            'flags': row['flags'], 'has_limit': row['has_limit'],
            'aliases': data['commands'][leaf]['aliases'],
            'choices': data['commands'][leaf]['choices'], 'scope': SCOPE}


def check(command):
    """Return fixed diagnostics, never echo credential-bearing option values."""
    import jmespath
    result = {'valid': False, 'issues': [], 'scope': SCOPE}
    def issue(code, flags=None):
        result['issues'].append({'code': code, **({'flags': sorted(flags)} if flags else {})})
    if not isinstance(command, str) or not 1 <= len(command) <= 16384:
        issue('command_size'); return result
    try:
        # Conservative exclusion of shell expansion; this checker never evaluates it.
        if '\n' in command or '\r' in command or '$(' in command or shell_substitution(command):
            issue('shell_composition'); return result
        lexer = shlex.shlex(command, posix=True, punctuation_chars=';&|()<>')
        lexer.whitespace_split = True
        tokens = list(lexer)
        if any(token in {';', '&&', '||', '|', '(', ')', '>', '<', '>>', '<<', '&'} for token in tokens):
            issue('shell_composition'); return result
        argv = shlex.split(command)
        if not argv or argv.pop(0) != 'oci':
            issue('not_one_oci_command'); return result
        leaf, raw = parse_oci(argv)
        contract = describe(leaf)
        if not contract['ok'] or not readonly_argv(argv):
            issue('not_approved_read'); return result
        result['leaf'] = leaf
        aliases = {**contracts()['globals']['aliases'], **contract['aliases']}
        options = {aliases.get(k, k): v for k, v in raw.items()}
        if len(options) != len(raw):
            issue('duplicate_alias')
        missing = set(contract['required']) - options.keys()
        if missing:
            issue('missing_required_options', missing)
        if {'--help', '--generate-full-command-json-input', '--generate-param-json-input'} & options.keys():
            issue('not_a_read_proposal')
        if '--all' in options:
            issue('unbounded_pagination', ['--all'])
        if contract['has_limit'] and '--limit' not in options:
            issue('missing_bounded_limit', ['--limit'])
        for flag in ('--limit', '--page-size'):
            if flag in options and (not re.fullmatch(r'[0-9]+', str(options[flag])) or not 1 <= int(options[flag]) <= 100):
                issue('invalid_page_bound', [flag])
        if '--query' not in options:
            issue('missing_query', ['--query'])
        else:
            try:
                jmespath.compile(options['--query'])
            except (ValueError, jmespath.exceptions.JMESPathError):
                issue('invalid_jmespath', ['--query'])
        choices = {**contracts()['globals']['choices'], **contract['choices']}
        for flag, spec in choices.items():
            if flag not in options or '$' in str(options[flag]):
                continue
            value = str(options[flag])
            allowed = [str(v) for v in spec['values']]
            if not spec['case_sensitive']:
                value, allowed = value.casefold(), [v.casefold() for v in allowed]
            if value not in allowed:
                issue('invalid_choice', [flag])
        result['valid'] = not result['issues']
    except (ValueError, TypeError, KeyError):
        issue('unknown_option_or_invalid_syntax')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['describe', 'check'])
    parser.add_argument('value')
    args = parser.parse_args()
    result = describe(args.value) if args.action == 'describe' else check(args.value)
    print(json.dumps(result, separators=(',', ':')))
    return int(not result.get('ok', result.get('valid', False)))


if __name__ == '__main__':
    raise SystemExit(main())
