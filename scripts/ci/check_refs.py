#!/usr/bin/env python3
"""Resolve local Markdown links and reject skill links into ../../docs."""

import re
from urllib.parse import unquote, urlsplit
from common import ROOT, arguments, files, finding, finish


def validate(path):
    if path.suffix != ".md" or "_TEMPLATE" in path.parts:
        return []
    result = []
    text = path.read_text()
    # Inline destinations and reference definitions. Ignore fenced examples.
    text = re.sub(r"(?ms)^(`{3,}|~{3,}).*?^\1[^\n]*", "", text)
    patterns = [
        r"\]\((<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)",
        r"(?m)^\s*\[[^]]+\]:\s*(<[^>]+>|\S+)",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            target = unquote(match[1].strip("<>"))
            link = urlsplit(target)
            if link.scheme or link.netloc or not link.path:
                continue
            line = text[: match.start()].count("\n") + 1
            if re.search(r"(^|/)\.\./\.\./docs(?:/|$)", link.path):
                result.append(finding(path, line, "cross_docs_reference"))
            if not (path.parent / link.path).exists():
                result.append(finding(path, line, "missing_reference"))
    if "references" in path.parts:
        if len(path.read_text().splitlines()) > 100 and not re.search(r"(?im)^#{1,3} (contents|table of contents|toc)\b", text):
            result.append(finding(path, 1, "reference_missing_toc"))
        if re.search(r"\]\([^)]*\.md(?:#[^)]*)?\)", text):
            result.append(finding(path, 1, "reference_chain"))
        if path.parent.name != "references":
            result.append(finding(path, 1, "reference_depth"))
    if path.name == 'SKILL.md':
        route = re.search(r'(?ms)^## Route\s*\n(.*?)(?=^## |\Z)', path.read_text())
        route_text = route[1] if route else ''
        for ref in sorted((path.parent / 'references').rglob('*.md')):
            if not any(ref.name in row and 'load when' in row.lower() for row in route_text.splitlines()):
                result.append(finding(ref, 1, 'unnamed_reference'))
    return result


def shared_findings(root=ROOT):
    routes = []
    for skill in (root / 'skills').glob('*/SKILL.md'):
        if skill.parent.name == '_TEMPLATE':
            continue
        match = re.search(r'(?ms)^## Route\s*\n(.*?)(?=^## |\Z)', skill.read_text())
        if match:
            routes.extend(match[1].splitlines())
    return [finding(ref, 1, 'unnamed_shared_reference') for ref in sorted((root / 'references').glob('*.md'))
            if ref.name != 'oci-doc-urls.md' and not any(ref.name in row and 'load when' in row.lower() for row in routes)]


def main():
    args = arguments(__doc__)
    selected = files(args.paths or [ROOT / "skills", ROOT / "references"])
    return finish(
        "refs", [f for p in selected for f in validate(p)] + (shared_findings() if not args.paths else []), args, len(selected)
    )


if __name__ == "__main__":
    raise SystemExit(main())
