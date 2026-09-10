#!/usr/bin/env python3
"""The single OCI subprocess door. Fixed JSON output, bounded reads, no shell evaluation."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from guard_lib import catalog_data, parse_oci, readonly_argv
from lib.sanitize import envelope, emit


class ReadOnlyRefusal(ValueError):
    pass


def check(argv):
    """Pure policy check. File-backed arguments must be resolved by the caller first."""
    return (True, 'read-only') if readonly_argv(argv) else (False, 'verb|method|flag')


def resolve_json(argv):
    path, opts = parse_oci(argv)
    value = opts.get('--from-json')
    if value is None:
        return list(argv)
    if not isinstance(value, str) or not value.startswith('file://'):
        raise ReadOnlyRefusal('flag')
    source = Path(value[7:]).expanduser()
    if source.stat().st_size > 1048576:
        raise ReadOnlyRefusal('flag')
    data = json.loads(source.read_text())
    if not isinstance(data, dict):
        raise ReadOnlyRefusal('flag')
    leaves, _ = catalog_data()
    # Only actual leaf flags are accepted; globals, command paths and opaque nested
    # data cannot change interpretation. CLI flags explicitly supplied win.
    flags = leaves.get(path, {}).get('flags', [])
    spellings = {flag[2:].replace('-', '').lower(): flag for flag in flags}
    result = path.split()
    for key, item in data.items():
        flag = spellings.get(key.replace('-', '').lower())
        if not flag or flag in {'--from-json', '--force'} or isinstance(item, (dict, list)):
            raise ReadOnlyRefusal('flag')
        if flag not in opts:
            opts[flag] = item
    opts.pop('--from-json', None)
    booleans = set(leaves.get(path, {}).get('boolean_flags', []))
    for flag, value in opts.items():
        if flag in booleans:
            if value is True:
                result.append(flag)
            elif value is not False:
                raise ReadOnlyRefusal('flag')
        else:
            result.extend([flag, str(value)])
    return result


def prepare(argv, *, profile=None, region=None, allow_all=False):
    try:
        argv = resolve_json(argv)
        if not check(argv)[0]:
            raise ReadOnlyRefusal('verb|method|flag')
        path, opts = parse_oci(argv)
        row = catalog_data()[0].get(path, {})
        if '--all' in opts and not (allow_all or os.environ.get('OCI_RO_ALLOW_ALL') == '1'):
            raise ReadOnlyRefusal('flag')
        for flag, value in (('--profile', profile), ('--region', region)):
            if value is not None and flag not in opts:
                argv.extend([flag, value])
        if '--output' in opts and opts['--output'] != 'json':
            raise ReadOnlyRefusal('flag')
        if '--output' not in opts:
            argv.extend(['--output', 'json'])
        if row.get('has_limit') and not {'--limit', '--all'} & opts.keys() and '--help' not in opts:
            argv.extend(['--limit', '100'])
        scope = os.environ.get('OCI_RO_SMOKE_SCOPE')
        if scope:
            _, bounded = parse_oci(argv)
            if ('--all' in bounded or bounded.get('--compartment-id-in-subtree', 'false').lower() != 'false'
                    or path == 'raw-request' or '--endpoint' in bounded):
                raise ReadOnlyRefusal('flag')
            for flag in ('--compartment-id', '--tenant-id', '--tenancy-id'):
                if flag in bounded and bounded[flag] != scope:
                    raise ReadOnlyRefusal('scope')
            for flag, key in (('--profile','OCI_RO_SMOKE_PROFILE'), ('--region','OCI_RO_SMOKE_REGION')):
                if bounded.get(flag) != os.environ.get(key):
                    raise ReadOnlyRefusal('scope')
            for flag, value in (('--no-retry', None), ('--connection-timeout','5'), ('--read-timeout','20')):
                if flag not in bounded:
                    argv.extend([flag] + ([value] if value else []))
        return ['--cli-rc-file', os.devnull, *argv]
    except (ValueError, OSError, KeyError, TypeError) as exc:
        raise ReadOnlyRefusal('verb|method|flag') from exc


def run_process(argv, *, executable=None, **kwargs):
    """Internal compatibility for help/validation consumers; errors remain local."""
    prepared = prepare(argv, profile=kwargs.pop('profile', None), region=kwargs.pop('region', None), allow_all=kwargs.pop('allow_all', False))
    environment = dict(kwargs.pop('env', os.environ))
    for key in ('OCI_CLI_AUTO_PROMPT', 'OCI_CLI_ENDPOINT', 'OCI_ENDPOINT',
                'OCI_CLI_RC_FILE', 'OCI_CLI_DEFAULTS_FILE'):
        environment.pop(key, None)
    if kwargs.pop('shell', False):
        raise ReadOnlyRefusal('flag')
    if os.environ.get('OCI_RO_TRACE') == '1':
        print(emit({'argv': ['oci', *prepared]}), file=sys.stderr)
    return subprocess.run([*(executable or ['oci']), *prepared], env=environment, shell=False, **kwargs)


def run(argv, *, profile=None, region=None, timeout=60, sanitize=True, allow_all=False):
    """Read once; blank successful list/summarize output means an empty collection.

    sanitize=False exposes that collection as data=[]; the default retains the
    untrusted-output envelope with items=[]. Nonempty malformed JSON is preserved
    for callers to reject, and failed reads never become empty successes.
    """
    from redact import redact
    try:
        prepared = prepare(argv, profile=profile, region=region, allow_all=allow_all)
        for attempt in range(3):
            response = run_process(argv, profile=profile, region=region, allow_all=allow_all,
                                   timeout=timeout, capture_output=True, text=True)
            try:
                err = json.loads(response.stderr[response.stderr.index('{'):]) if response.returncode else {}
            except (ValueError, TypeError):
                err = {}
            if not response.returncode or err.get('status') != 429 or attempt == 2:
                break
            time.sleep(2 ** attempt)
        safe_argv = [redact(v) for v in prepared]
        if response.returncode:
            status = None
            try:
                error = json.loads(response.stderr[response.stderr.index('{'):])
                status = error.get('status') if isinstance(error.get('status'), int) else None
            except (ValueError, TypeError, AttributeError):
                pass
            return {'ok': False, 'error': {'kind': 'service', 'status': status, **({'code': 'LifecyclePolicyNotFound'} if err.get('code') == 'LifecyclePolicyNotFound' else {})}, 'argv': safe_argv, 'truncated': False}
        try:
            path, _ = parse_oci(prepared)
            operation = path.rsplit(' ', 1)[-1]
            collection = (operation in {'list', 'summarize'}
                          or operation.startswith(('list-', 'summarize-', 'request-summarized-'))
                          or operation.endswith('-list'))
            payload = json.loads(response.stdout) if response.stdout.strip() else ([] if collection else None)
        except ValueError:
            payload = response.stdout
        data = envelope(payload, source='oci:cli:read', kind='generic', complete=False) if sanitize else payload
        # Redaction is applied after cleaning, including nested returned values.
        def visit(value):
            if isinstance(value, dict):
                return {k: visit(v) for k, v in value.items()}
            if isinstance(value, list):
                return [visit(v) for v in value]
            return redact(value) if isinstance(value, str) else value
        data = visit(data)
        flags = data.get('flags', []) if isinstance(data, dict) else []
        _, options = parse_oci(prepared)
        rows = payload
        for key in ('data', 'items'):
            if isinstance(rows, dict) and key in rows:
                rows = rows[key]
        limit = int(options['--limit']) if '--limit' in options else None
        saturated = bool(limit and isinstance(rows, list) and len(rows) >= limit)
        # Filtered projections can shrink a full page: preserve the CLI pagination warning too.
        pagination_warning = 'not all resources were returned' in response.stderr.lower()
        return {'ok': True, 'data': data, 'argv': safe_argv, 'truncated': saturated or pagination_warning or 'truncated' in flags or bool(isinstance(payload, dict) and payload.get('opc-next-page')), 'page_saturated': saturated}
    except ReadOnlyRefusal:
        return {'ok': False, 'error': {'kind': 'refused', 'reason': 'verb|method|flag'}, 'argv': [], 'truncated': False}
    except (OSError, subprocess.TimeoutExpired):
        return {'ok': False, 'error': {'kind': 'transport', 'status': None}, 'argv': [], 'truncated': False}
    except Exception:
        return {'ok': False, 'error': {'kind': 'internal', 'status': None}, 'argv': [], 'truncated': False}


def main():
    argv = sys.argv[1:]
    if '--' in argv:
        split = argv.index('--')
        options, argv = argv[:split], argv[split + 1:]
        if set(options) - {'--sanitize', '--trace'}:
            print(emit({'error': 'refused', 'reason': 'flag', 'op': ''}))
            return 3
        if '--trace' in options:
            os.environ['OCI_RO_TRACE'] = '1'
    result = run(argv)
    if result['ok']:
        print(emit(result))
        return 0
    error = result['error']
    if error['kind'] == 'refused':
        print(emit({'error': 'refused', 'reason': error['reason'], 'op': ''}))
        return 3
    print(emit(error), file=sys.stderr)
    return 2 if error['kind'] == 'internal' else 1


if __name__ == '__main__':
    sys.exit(main())
