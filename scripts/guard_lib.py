"""Conservative shell inspection, never shell execution. Advisory; IAM is the boundary."""
import json
import re
import shlex
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RANK = {'allow': 0, 'ask': 1, 'deny': 2}


@lru_cache(maxsize=1)
def catalog_data():
    rows = [json.loads(line) for line in (ROOT / 'catalog/cli.jsonl').read_text().splitlines()]
    meta = json.loads((ROOT / 'catalog/cli-meta.json').read_text())
    return {r['path']: r for r in rows}, meta['global_options']


@lru_cache(maxsize=1)
def rules():
    return json.loads((ROOT / 'catalog/guard.json').read_text())


def parse_oci(argv):
    """Resolve a known leaf using option arity, including global options before the path."""
    leaves, global_options = catalog_data()
    path, options = [], {}
    index = 0
    while index < len(argv):
        token = argv[index]
        if token.startswith('-'):
            flag, equal, value = token.partition('=')
            row = leaves.get(' '.join(path), {})
            flags = set(global_options['flags']) | set(row.get('flags', []))
            booleans = set(global_options['boolean_flags']) | set(row.get('boolean_flags', []))
            if flag not in flags or flag in options:
                raise ValueError('Unknown or duplicate option')
            if flag not in booleans and not equal:
                index += 1
                if index >= len(argv) or argv[index].startswith('--'):
                    raise ValueError('Missing option value')
                value = argv[index]
            options[flag] = value if (equal or flag not in booleans) else True
        else:
            path.append(token)
        index += 1
    return ' '.join(path), options


def readonly_argv(argv):
    try:
        path, opts = parse_oci(argv)
        leaves, _ = catalog_data()
        # Endpoint/config aliases and prompt modes can alter interpretation or execution.
        forbidden = {'--endpoint', '--cli-auto-prompt', '--cli-rc-file', '--defaults-file',
                     '--from-json', '--debug', '--proxy', '--federation-endpoint', '--force'}
        if forbidden & opts.keys():
            return False
        if any(k in opts for k in ('--help', '-h', '-?')):
            return path in leaves or any(p.startswith(path + ' ') for p in leaves) or not path
        if '--generate-full-command-json-input' in opts or '--generate-param-json-input' in opts:
            return path in leaves
        return bool(leaves.get(path, {}).get('read_only'))
    except (ValueError, OSError, KeyError):
        return False


def classify_leaf(path):
    rule = rules()
    if any(re.search(pattern, path) for pattern in rule['tier_block']):
        return 'deny'
    op = path.split()[-1]
    if (re.match(rule['op_read_extra'], op) or
            (not re.match(rule['op_write_prefix'], op) and
             (re.match(rule['op_read'], op) or re.search(rule['op_read_suffix'], op)))):
        return 'allow'
    return 'ask'


def classify_oci(argv):
    try:
        path, opts = parse_oci(argv)
    except ValueError:
        return 'ask'
    if any(k in opts for k in ('--help', '-h', '-?')) and readonly_argv(argv):
        return 'allow'
    if '--force' in opts or any(k.startswith('--empty-bucket') for k in opts) or 'bulk-delete' in path:
        return 'ask'
    if '--from-json' in opts:
        # JSON can override request data. Do not open arbitrary files from a tool payload.
        return 'ask'
    if path == 'raw-request':
        return 'allow' if opts.get('--http-method', '').upper() in ('GET', 'HEAD') else 'ask'
    leaves, _ = catalog_data()
    if path not in leaves:
        return 'ask'
    return classify_leaf(path)


def shell_segments(command):
    lexer = shlex.shlex(command, posix=True, punctuation_chars=';&|()<>\n')
    lexer.whitespace = ' \t\r'
    lexer.whitespace_split = True
    segment = []
    for token in lexer:
        if token and all(c in ';&|()<>\n' for c in token):
            if segment:
                yield segment
            segment = []
        else:
            segment.append(token)
    if segment:
        yield segment


def inspect_command(command):
    if not isinstance(command, str) or len(command) > 131072:
        return 'ask'
    # These forms need shell evaluation to resolve; this advisory parser never evaluates them.
    opaque = re.search(r'`|\$\(|<\(|>\(|\beval\b|\b(base64|xxd)\b|\b(?:ba|da|z|k)?sh\s+-|\b(?:python[\d.]*|perl|ruby|node)\s+.*-[ce]\b', command)
    decisions = ['ask'] if opaque else []
    try:
        for argv in shell_segments(command):
            joined = ' '.join(argv)
            if any(re.search(pattern, joined, re.I) for pattern in rules()['non_oci_ask']):
                decisions.append('ask')
            if any(t == '.' or Path(t).name in {'sh', 'bash', 'dash', 'zsh', 'source', '.'} for t in argv):
                decisions.append('ask')
            oci_indexes = [i for i, t in enumerate(argv) if Path(t).name == 'oci']
            for i in oci_indexes:
                tail = argv[i + 1:]
                decisions.append(classify_oci(tail))
            for i, token in enumerate(argv):
                if '/scripts/' in token and ('CLAUDE_PLUGIN_ROOT' in token or token.startswith(str(ROOT))):
                    decisions.append('allow' if readonly_argv(argv[i + 1:]) else 'deny')
            if not oci_indexes and any('$' in t and 'CLAUDE_PLUGIN_ROOT}/scripts/' not in t for t in argv[:1]):
                decisions.append('ask')
    except (ValueError, OSError, KeyError):
        return 'ask'
    return max(decisions, key=RANK.get, default='allow')
