#!/usr/bin/env python3
"""Reject credential-shaped material and symlinks in tracked or explicitly supplied files."""

import re
import subprocess
from common import ROOT, arguments, finding, finish

PATTERNS = {
    "real_ocid": r"ocid1\.[a-z0-9_-]+\.[a-z0-9]+\.[a-z0-9-]*\.[A-Za-z0-9_-]{20,}",
    "private_key": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\r\n]",
    "jwt": r"\beyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}",
    "aws_key": r"\bAKIA[A-Z0-9]{16}\b",
    "assigned_secret": r"(?i)\b(?:password|auth_token|api_key|access_token)\s*[:=]\s*[\"\x27][A-Za-z0-9+/=_-]{20,}[\"\x27]",
}


def validate(path):
    if path.is_symlink():
        return [finding(path, 1, "symlink")]
    if not path.is_file():
        return []
    text = path.read_bytes().decode("utf-8", errors="replace")
    return [
        finding(path, text[: m.start()].count("\n") + 1, name)
        for name, pattern in PATTERNS.items()
        for m in re.finditer(pattern, text)
    ]


def main():
    args = arguments(__doc__)
    if args.paths:
        selected = [
            file for p in args.paths for file in (p.rglob("*") if p.is_dir() else [p])
        ]
    else:
        selected = [
            ROOT / p
            for p in subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
            .decode()
            .split("\0")
            if p
        ]
    return finish(
        "secrets", [f for p in selected for f in validate(p)], args, len(selected)
    )


if __name__ == "__main__":
    raise SystemExit(main())
