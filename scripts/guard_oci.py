#!/usr/bin/env python3
"""PreToolUse Bash advisory guard: JSON in, permission decision out; deny exits 2."""
import json
import sys


def main():
    decision = 'ask'
    reason = 'Command requires review. Advisory guard; IAM is the boundary.'
    try:
        from redact import redact
        from guard_lib import inspect_command
        raw = sys.stdin.read(131073)
        if '--stdin-argv' in sys.argv[1:]:
            import shlex
            argv = json.loads(raw)
            if not isinstance(argv, list) or not all(isinstance(v, str) for v in argv):
                raise ValueError('Expected JSON argv array')
            payload = {'tool_name': 'Bash', 'tool_input': {'command': shlex.join(argv)}}
        else:
            payload = json.loads(raw)
        if payload.get('tool_name') == 'Bash':
            decision = inspect_command(payload['tool_input']['command'])
        reason = redact({
            'allow': 'Read operation or unrelated command. Advisory guard; IAM is the boundary.',
            'ask': reason,
            'deny': 'Blocked operation. Use list/get to inspect state. Advisory guard; IAM is the boundary.',
        }[decision])
    except Exception:
        decision = 'ask'
    print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse',
          'permissionDecision': decision, 'permissionDecisionReason': reason}}))
    return 2 if decision == 'deny' else 0


if __name__ == '__main__':
    sys.exit(main())
