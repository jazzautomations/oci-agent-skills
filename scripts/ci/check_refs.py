#!/usr/bin/env python3
"""Resolve local Markdown links and reject skill links into ../../docs."""
import re
from urllib.parse import unquote, urlsplit
from common import arguments, files, finding, finish


def validate(path):
    result = []
    text = path.read_text()
    # Inline destinations and reference definitions. Ignore fenced examples.
    text = re.sub(r'(?ms)^(`{3,}|~{3,}).*?^\1[^\n]*', '', text)
    patterns = [r'\]\((<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)', r'(?m)^\s*\[[^]]+\]:\s*(<[^>]+>|\S+)']
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            target = unquote(match[1].strip('<>'))
            link = urlsplit(target)
            if link.scheme or link.netloc or not link.path:
                continue
            line = text[:match.start()].count('\n') + 1
            if re.search(r'(^|/)\.\./\.\./docs(?:/|$)', link.path):
                result.append(finding(path, line, 'cross_docs_reference'))
            if not (path.parent / link.path).exists():
                result.append(finding(path, line, 'missing_reference'))
    return result


def main():
    args = arguments(__doc__)
    selected = files(args.paths)
    return finish('refs', [f for p in selected for f in validate(p)], args, len(selected))


if __name__ == '__main__':
    raise SystemExit(main())
