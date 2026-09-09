"""Conservative shell inspection, never shell execution. Advisory; IAM is the boundary."""
import hashlib
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
        forbidden = {'--cli-auto-prompt', '--cli-rc-file', '--defaults-file',
                     '--from-json', '--debug', '--proxy', '--federation-endpoint', '--force'}
        if forbidden & opts.keys():
            return False
        if any(k in opts for k in ('--help', '-h', '-?')):
            return path in leaves or any(p.startswith(path + ' ') for p in leaves) or not path
        if '--generate-full-command-json-input' in opts or '--generate-param-json-input' in opts:
            return path in leaves
        if path == 'raw-request':
            return opts.get('--http-method', '').upper() in {'GET', 'HEAD'} and bool(opts.get('--target-uri'))
        return bool(leaves.get(path, {}).get('read_only'))
    except (ValueError, OSError, KeyError):
        return False


def classify_leaf(path):
    rule = rules()
    if any(re.search(pattern, path) for pattern in rule['tier_block']):
        return 'deny'
    leaves, _ = catalog_data()
    if not leaves.get(path, {}).get('read_only'):
        return 'ask'
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
        # Malformed options cannot weaken a resolved blocked leaf.
        for end in range(len(argv), 0, -1):
            try:
                prefix, _ = parse_oci(argv[:end])
                if prefix in catalog_data()[0] and classify_leaf(prefix) == 'deny':
                    return 'deny'
            except ValueError:
                continue
        return 'ask'
    if any(k in opts for k in ('--help', '-h', '-?')) and readonly_argv(argv):
        return 'allow'
    leaves, _ = catalog_data()
    tier = classify_leaf(path) if path in leaves else 'ask'
    if path == 'raw-request':
        tier = 'allow' if readonly_argv(argv) else 'ask'
    dangerous = '--force' in opts or any(k.startswith('--empty-bucket') for k in opts) or 'bulk-delete' in path
    if dangerous:
        tier = {'allow': 'ask', 'ask': 'deny', 'deny': 'deny'}[tier]
    if '--from-json' in opts:
        tier = max(tier, 'ask', key=RANK.get)
    return tier


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


def plugin_path(token):
    """Recognize plugin-root paths without shell expansion or basename guessing."""
    return (token.startswith(('${CLAUDE_PLUGIN_ROOT}/', '$CLAUDE_PLUGIN_ROOT/', str(ROOT) + '/')) or
            bool(re.match(r'^(?:\./)?(?:scripts/|skills/[^/]+/scripts/)', token)))


def plugin_script(token, argv):
    """Unknown/changed scripts require review; a digest is provenance, not a sandbox."""
    from lib.oci_ro import check
    expanded = token.replace('${CLAUDE_PLUGIN_ROOT}', str(ROOT)).replace('$CLAUDE_PLUGIN_ROOT', str(ROOT))
    try:
        path = Path(expanded)
        if not path.is_absolute():
            path = ROOT / path
        if path.is_symlink():
            return 'ask'
        relative = path.resolve().relative_to(ROOT.resolve()).as_posix()
        raw = (ROOT / 'catalog/scripts.json').read_bytes()
        if hashlib.sha256(raw).hexdigest() != rules().get('scripts_sha256'):
            return 'ask'
        rows = json.loads(raw)['scripts']
        row = next((r for r in rows if r['path'] == relative), None)
        if not row or row['mode'] != 'read-only' or hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
            return 'ask'
        if relative in {'scripts/lib/oci_ro.py', 'scripts/lib/oci_ro.sh'}:
            tail = argv[argv.index('--') + 1:] if '--' in argv else argv
            return 'allow' if check(tail)[0] else 'ask'
        skip_value = False
        for value in argv:
            if skip_value:
                skip_value = False
                continue
            if value in {'--profile', '--auth'}:
                skip_value = True
                continue
            if value.startswith(('--profile=', '--auth=')):
                continue
            if re.match(rules()['op_write_prefix'], value.lstrip('-')):
                return 'ask'
            if any(re.search(pattern, value) for pattern in rules()['tier_block']):
                return 'ask'
        return 'allow'
    except (ValueError, OSError, KeyError, TypeError):
        return 'ask'


def inspect_command(command):
    if not isinstance(command, str) or len(command) > 131072:
        return 'ask'
    # These forms need shell evaluation to resolve; this advisory parser never evaluates them.
    opaque = re.search(r'`|\$\(|<\(|>\(|\beval\b|\b(base64|xxd)\b|(?<![\w./-])(?:/(?:[^\s/]+/)*)?(?:ba|da|z|k)?sh\s+-|\b(?:python[\d.]*|perl|ruby|node)\s+.*-[ce]\b', command)
    decisions = ['ask'] if opaque else []
    unclassified = False
    try:
        for argv in shell_segments(command):
            before = len(decisions)
            joined = ' '.join(argv)
            if any(re.search(pattern, joined, re.I) for pattern in rules()['non_oci_ask']):
                decisions.append('ask')
            script_indexes = [i for i, token in enumerate(argv) if plugin_path(token) and
                              (i == 0 or Path(argv[i - 1]).name in {'python', 'python3', 'bash', 'sh', 'env', 'sudo'})]
            if any(t == '.' or Path(t).name in {'sh', 'bash', 'dash', 'zsh', 'source', '.'} for t in argv) and not script_indexes:
                decisions.append('ask')
            oci_indexes = [i for i, t in enumerate(argv) if Path(t).name == 'oci']
            for i in oci_indexes:
                tail = argv[i + 1:]
                decisions.append(classify_oci(tail))
            for i in script_indexes:
                decisions.append(plugin_script(argv[i], argv[i + 1:]))
            if not oci_indexes and '$' in argv[0] and 0 not in script_indexes:
                decisions.append('ask')
            if len(decisions) == before:
                unclassified = True
    except (ValueError, OSError, KeyError):
        return 'ask'
    decision = max(decisions, key=RANK.get, default=None)
    return None if decision == 'allow' and unclassified else decision
