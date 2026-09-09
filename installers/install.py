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
    "evals",
    "installers",
    ".claude-plugin",
    ".codex-plugin",
    ".mcp.json",
    "LICENSE",
    "NOTICE",
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
            "vendor",
            "_TEMPLATE",
            "CODEX-STATUS.md",
            "node_modules",
        }
        or name.startswith((".env", ".handoff-"))
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


def materialize_shared(staging):
    """Copy root shared references into each skill with collision-free depth-one names."""
    shared = staging / 'references'
    if not shared.is_dir():
        return
    for skill in sorted((staging / 'skills').iterdir()):
        if not skill.is_dir() or skill.name.startswith('_'):
            continue
        refs = skill / 'references'
        refs.mkdir(exist_ok=True)
        mapping = {p.name: 'shared-' + p.name for p in shared.iterdir() if p.is_file()}
        for source in sorted(shared.iterdir()):
            if not source.is_file():
                raise ValueError('Shared references must have depth one')
            target = refs / mapping[source.name]
            if target.exists():
                raise ValueError('Shared reference copy would overwrite a skill file')
            copy_payload(source, target)
            if source.suffix == '.md':
                text = target.read_text()
                for old, new in mapping.items():
                    text = text.replace('](' + old, '](' + new)
                target.write_text(text)
        for markdown in skill.rglob('*.md'):
            text = markdown.read_text()
            for old, new in mapping.items():
                text = text.replace('../../references/' + old, 'references/' + new if markdown.parent == skill else new)
            markdown.write_text(text)


def install(target, host="all", *, accept_unguarded=False, copy_shared=False):
    if host != 'claude' and not accept_unguarded:
        raise ValueError('UNGUARDED host: --i-accept-unguarded is required; the Bash guard is unavailable')
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
        if copy_shared:
            materialize_shared(staging)
        selected = list(HOSTS) if host == "all" else ([] if host == "claude" else [host])
        host_configs(staging, target, selected)
        os.replace(staging, target)
    return {"ok": True, "hosts": selected or ["claude"], "copy_only": True,
            "guard": "guarded: advisory Bash PreToolUse" if host == "claude" else "UNGUARDED: no automatic Bash guard",
            "shared_copied": copy_shared,
            "runtime_setup": ["uv", "sync", "--frozen", "--project", str(target / "runtime")],
            "runtime_note": "Run runtime_setup before starting the host. Otherwise the first MCP launch installs the target environment and requires package access."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--host", choices=["all", "claude", *HOSTS], default="all")
    parser.add_argument("--i-accept-unguarded", action="store_true")
    parser.add_argument("--copy-shared", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(install(args.target, args.host, accept_unguarded=args.i_accept_unguarded, copy_shared=args.copy_shared)))
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
