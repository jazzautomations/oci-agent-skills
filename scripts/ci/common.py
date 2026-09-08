"""Shared deterministic validator reporting and explicit legacy-debt comparison."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def arguments(description, live=False):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument(
        "--baseline",
        type=Path,
        help="Accept only exactly recorded legacy findings; never new findings.",
    )
    if live:
        parser.add_argument("--live-help", action="store_true")
    return parser.parse_args()


def files(paths):
    result = []
    for path in paths or [ROOT / "skills"]:
        result.extend(path.rglob("*.md") if path.is_dir() else [path])
    return sorted(set(result))


def finding(path, line, code):
    try:
        name = str(path.resolve().relative_to(ROOT))
    except ValueError:
        name = path.name
    return {"file": name, "line": line, "code": code}


def finish(name, findings, args, checked):
    findings = sorted(findings, key=lambda f: (f["file"], f["line"], f["code"]))
    baseline = (
        json.loads(args.baseline.read_text()).get(name, []) if args.baseline else []
    )
    # A stale exemption fails too, so a content owner must retire it when fixing a skill.
    ok = findings == baseline
    print(
        json.dumps(
            {
                "validator": name,
                "checked": checked,
                "findings": findings,
                "baseline_matches": ok if args.baseline else None,
                "ok": ok,
            },
            indent=2,
        )
    )
    return 0 if ok else 1
