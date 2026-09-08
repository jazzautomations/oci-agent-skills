#!/usr/bin/env python3
"""Nightly Oracle documentation URL liveness; no OCI API operations."""

import argparse
import concurrent.futures
import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from common import ROOT, files


def urls(text):
    return set(re.findall(r'https://docs\.oracle\.com/[^\s<>`"\])]+', text))


def status(url):
    try:
        with urlopen(
            Request(url, headers={"User-Agent": "oci-agent-skills-link-check/0.2.1"}),
            timeout=20,
        ) as response:
            return response.status
    except HTTPError as exc:
        return exc.code
    except (URLError, TimeoutError, OSError):
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=__import__("pathlib").Path)
    parser.add_argument(
        "--offline", action="store_true", help="List URLs without HTTP requests"
    )
    parser.add_argument(
        "--negative-fixtures",
        type=__import__("pathlib").Path,
        default=ROOT / "scripts/ci/link-negatives.json",
    )
    args = parser.parse_args()
    negatives = json.loads(args.negative_fixtures.read_text())
    selected = set().union(
        *(
            urls(p.read_text())
            for p in files(
                args.paths
                or [
                    ROOT / "skills",
                    ROOT / "references",
                    ROOT / "docs",
                    ROOT / "README.md",
                ]
            )
        )
    )
    if args.offline:
        print(
            json.dumps(
                {"urls": sorted(selected), "negative_fixtures": negatives}, indent=2
            )
        )
        return 0
    targets = sorted(selected | set(negatives))
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = [
            {"url": url, "status": code, "expected": negatives.get(url, 200)}
            for url, code in zip(targets, pool.map(status, targets))
        ]
    ok = all(row["status"] == row["expected"] for row in results)
    print(json.dumps({"ok": ok, "results": results}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
