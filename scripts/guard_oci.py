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
        payload = json.loads(sys.stdin.read(131073))
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
