#!/usr/bin/env python3
"""Copy the plugin and project-local host configuration into a new/empty target."""

import argparse
import json
import os
import re
import shutil
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

SOURCE = Path(__file__).resolve().parents[1]
PAYLOAD = (
    "skills",
    "references",
    "scripts",
    "hooks",
    "catalog",
    "runtime",
    "docs",
    "installers",
    ".claude-plugin",
    ".codex-plugin",
    ".mcp.json",
    "LICENSE",
    "README.md",
)
HOSTS = {
    "codex": ".agents",
    "gemini": ".gemini",
    "cursor": ".cursor",
    "opencode": ".opencode",
}


def ignored(name):
    return (
        name
        in {
            ".venv",
            "__pycache__",
            ".pytest_cache",
            ".ruff_cache",
            ".git",
            "research",
            "node_modules",
        }
        or name.startswith(".env")
        or name.endswith((".pyc", ".pem", ".key", ".tfstate", ".tfplan"))
    )


def copy_payload(source, target):
    if source.is_symlink():
        raise ValueError("Package source contains a symlink")
    if source.is_dir():
        target.mkdir(parents=True, exist_ok=True)
        for child in sorted(source.iterdir()):
            if not ignored(child.name):
                copy_payload(child, target / child.name)
    elif source.is_file():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def relocate_links(text, original, destination, root):
    def replace(match):
        target = match[1]
        parsed = urlsplit(unquote(target.strip("<>")))
        if parsed.scheme or parsed.netloc or not parsed.path:
            return match[0]
        resolved = (original.parent / parsed.path).resolve()
        if not resolved.is_relative_to(root):
            raise ValueError("Skill reference escapes installed plugin")
        relative = Path(os.path.relpath(resolved, destination.parent)).as_posix()
        if parsed.fragment:
            relative += "#" + parsed.fragment
        return (
            "]("
            + ("<" + relative + ">" if target.startswith("<") else relative)
            + match[2]
        )

    return re.sub(r"\]\((<[^>]+>|[^\s)]+)(\s+[^)]*\)|\))", replace, text)


def host_configs(staging, final, selected):
    args = ["run", "--frozen", "--project", str(final / "runtime"), "oci-readonly-mcp"]
    command = {"command": "uv", "args": args}
    for host in selected:
        skill_root = staging / HOSTS[host] / "skills"
        for skill in sorted((staging / "skills").iterdir()):
            if not skill.is_dir() or skill.name.startswith("_"):
                continue
            destination = skill_root / skill.name
            copy_payload(skill, destination)
            for markdown in destination.rglob("*.md"):
                original = skill / markdown.relative_to(destination)
                markdown.write_text(
                    relocate_links(markdown.read_text(), original, markdown, staging)
                )
        if host == "codex":
            path = staging / ".codex/config.toml"
            path.parent.mkdir(exist_ok=True)
            path.write_text(
                '[mcp_servers.oci-readonly]\ncommand = "uv"\nargs = '
                + json.dumps(args, ensure_ascii=False)
                + "\nstartup_timeout_sec = 60\n"
            )
        elif host in {"gemini", "cursor"}:
            path = staging / (
                ".gemini/settings.json" if host == "gemini" else ".cursor/mcp.json"
            )
            path.parent.mkdir(exist_ok=True)
            spec = {**command, **({"type": "stdio"} if host == "cursor" else {})}
            path.write_text(
                json.dumps({"mcpServers": {"oci-readonly": spec}}, indent=2) + "\n"
            )
        else:
            # OpenCode v2 schema. v1 requires a different mcp nesting.
            (staging / "opencode.json").write_text(
                json.dumps(
                    {
                        "$schema": "https://opencode.ai/config.json",
                        "mcp": {
                            "servers": {
                                "oci-readonly": {
                                    "type": "local",
                                    "command": ["uv", *args],
                                }
                            }
                        },
                    },
                    indent=2,
                )
                + "\n"
            )


def install(target, host="all"):
    target = target.expanduser().absolute()
    if any(p.is_symlink() for p in [target, *target.parents]):
        raise ValueError("Target path must not contain symlinks")
    target = target.resolve()
    if (
        target == SOURCE
        or target.is_relative_to(SOURCE)
        or SOURCE.is_relative_to(target)
    ):
        raise ValueError("Target must be outside the source tree")
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        raise ValueError(
            "Target must be absent or empty; existing files are never overwritten"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=".oci-install-", dir=target.parent
    ) as directory:
        staging = Path(directory) / "payload"
        staging.mkdir()
        for name in PAYLOAD:
            if (SOURCE / name).exists():
                copy_payload(SOURCE / name, staging / name)
        selected = list(HOSTS) if host == "all" else [host]
        host_configs(staging, target, selected)
        os.replace(staging, target)
    return {"ok": True, "hosts": selected, "copy_only": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--host", choices=["all", *HOSTS], default="all")
    args = parser.parse_args()
    try:
        print(json.dumps(install(args.target, args.host)))
    except (OSError, ValueError) as exc:
        # Paths can contain private usernames; fixed errors only.
        message = (
            str(exc)
            if isinstance(exc, ValueError)
            else "Unable to copy the installation"
        )
        print(json.dumps({"ok": False, "error": message}))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
