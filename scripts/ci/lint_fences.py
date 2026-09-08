#!/usr/bin/env python3
"""Check fenced OCI commands against the snapshot; --live-help executes help only."""

import re
import shlex
import sys
from common import ROOT, arguments, files, finding, finish

sys.path.insert(0, str(ROOT / "scripts"))
from guard_lib import catalog_data, parse_oci
from lib.oci_ro import run


def commands(text):
    fence = None
    accumulated = ""
    start = 0
    for number, line in enumerate(text.splitlines(), 1):
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if match:
            if fence and match[1][0] == fence:
                fence = None
            elif not fence:
                fence = match[1][0]
            continue
        if not fence:
            continue
        if not accumulated:
            start = number
        accumulated += line.strip().removeprefix("$ ") + " "
        if line.rstrip().endswith("\\"):
            accumulated = accumulated.rstrip()[:-1] + " "
            continue
        if accumulated.strip().startswith("oci "):
            yield start, accumulated.strip()
        accumulated = ""


def validate(path, live=False):
    result = []
    leaves, _ = catalog_data()
    for line, command in commands(path.read_text()):
        try:
            argv = shlex.split(command, comments=True)[1:]
            leaf, options = parse_oci(argv)
            row = leaves.get(leaf)
            if row is None:
                raise ValueError("unknown_leaf")
            if not any(f in options for f in ("--help", "-h", "-?")):
                if set(row["required"]) - options.keys():
                    raise ValueError("missing_required_flags")
                if (
                    row["verb"].startswith("list")
                    and not {"--all", "--limit"} & options.keys()
                ):
                    raise ValueError("unbounded_list")
            if live:
                # Never execute the example: construct a fresh leaf-only --help argv.
                response = run(
                    [*leaf.split(), "--help"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if response.returncode or "Commands:" in response.stdout:
                    raise ValueError("live_help_failed")
                if any(flag not in response.stdout for flag in row["required"]):
                    raise ValueError("live_required_mismatch")
        except Exception as exc:
            code = (
                str(exc)
                if isinstance(exc, ValueError)
                and str(exc)
                in {
                    "unknown_leaf",
                    "missing_required_flags",
                    "unbounded_list",
                    "live_help_failed",
                    "live_required_mismatch",
                }
                else "invalid_command"
            )
            result.append(finding(path, line, code))
    return result


def main():
    args = arguments(__doc__, live=True)
    selected = files(args.paths)
    return finish(
        "fences",
        [f for p in selected for f in validate(p, args.live_help)],
        args,
        len(selected),
    )


if __name__ == "__main__":
    raise SystemExit(main())
