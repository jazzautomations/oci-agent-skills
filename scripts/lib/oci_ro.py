#!/usr/bin/env python3
"""The only OCI subprocess entry point for plugin scripts; refusals exit 3."""
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from guard_lib import readonly_argv


class ReadOnlyRefusal(ValueError):
    pass


def run(argv, *, executable=None, **kwargs):
    if not readonly_argv(argv):
        raise ReadOnlyRefusal('OCI command is outside the script read-only allowlist')
    environment = dict(kwargs.pop('env', os.environ))
    for key in ('OCI_CLI_AUTO_PROMPT', 'OCI_CLI_ENDPOINT', 'OCI_ENDPOINT',
                'OCI_CLI_RC_FILE', 'OCI_CLI_DEFAULTS_FILE'):
        environment.pop(key, None)
    if kwargs.pop('shell', False):
        raise ReadOnlyRefusal('Shell execution is unavailable')
    return subprocess.run([*(executable or ['oci']), '--cli-rc-file', os.devnull, *argv],
                          env=environment, shell=False, **kwargs)


def main():
    try:
        return run(sys.argv[1:]).returncode
    except ReadOnlyRefusal as exc:
        print(str(exc), file=sys.stderr)
        return 3
    except (OSError, ValueError):
        print('OCI read could not be started', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
