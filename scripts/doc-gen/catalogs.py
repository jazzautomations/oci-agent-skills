#!/usr/bin/env python3
"""Generate reader catalogs from shipped skills and offline MCP schemas."""

import argparse
import asyncio
from collections import Counter
from pathlib import Path
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parents[2]
DOMAINS = {
    "Navigation, identity & governance": (
        "oci-navigator", "oci-cli-auth", "oci-tenancy-governance", "oci-iam-policy",
        "oci-support-limits",
    ),
    "Compute, network & storage": (
        "oci-compute", "oci-networking", "oci-object-storage", "oci-block-file-storage",
        "oci-bastion-access",
    ),
    "Delivery & infrastructure as code": (
        "oci-oke", "oci-devops-pipelines", "oci-serverless", "oci-terraform",
    ),
    "Operations & security": (
        "oci-monitoring-alarms", "oci-logging-audit", "oci-incident-triage",
        "oci-security-posture", "oci-vault-certificates",
    ),
    "Cost & Free Tier": ("oci-cost-analysis", "oci-free-tier"),
    "Oracle Database & APEX": (
        "oracle-autonomous-db", "oracle-db-fleet", "oracle-db-vector-ai",
        "oracle-db-sql-access", "oracle-apex",
    ),
    "AI & data": ("oci-generative-ai", "oci-ai-services", "oci-data-platform"),
    "Reliability & migration": ("oci-dr-backup", "oci-migration-patching"),
    "SDKs & enterprise applications": ("oci-sdk-patterns", "oracle-enterprise-apps"),
}


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def load_skills(root=ROOT):
    skills = {}
    for path in sorted((root / "skills").glob("*/SKILL.md")):
        if path.parent.name.startswith("_"):
            continue
        text = path.read_text()
        data = yaml.safe_load(text.split("---", 2)[1])
        description = data["description"]
        purpose, triggers = description.split(" Use when:", 1)
        use, exclude = triggers.split(" Not for:", 1)
        commands = re.search(r"(?ms)^## Commands\s*\n(.*?)(?=^## |\Z)", text)
        # Quote only reads, preserving the full fence's scope flags and variables.
        samples = []
        if commands:
            for body in re.findall(r"(?ms)^```[^\n]*\n(.*?)^```", commands[1]):
                if "MUTATING" not in body and re.search(r"(?m)^oci ", body):
                    samples.append(body.strip())
        shared = sorted(set(re.findall(r"\.\./\.\./references/([A-Za-z0-9_.-]+)", text)))
        skills[data["name"]] = {
            "purpose": purpose.strip(), "use": use.strip(), "exclude": exclude.strip(),
            "mode": data["metadata"]["mode"], "verified": data["metadata"]["verified"],
            "scripts": len([p for p in (path.parent / "scripts").glob("*")
                            if p.is_file() and p.suffix in {".py", ".sh"}]),
            "references": len(list((path.parent / "references").glob("*.md"))),
            "shared": shared, "commands": samples[:3],
        }
    listed = [name for names in DOMAINS.values() for name in names]
    if len(listed) != len(set(listed)) or set(listed) != set(skills):
        raise ValueError("Domain map must contain every shipped skill exactly once")
    return skills


def skills_markdown(skills):
    modes = Counter(s["mode"] for s in skills.values())
    levels = Counter(s["verified"] for s in skills.values())
    lines = ["# Skills catalog", "", "[Documentation](README.md) · [MCP tools](mcp-tools.md)", "",
             "Generated from `skills/*/SKILL.md`; regenerate with "
             "`uv run --frozen --project runtime python scripts/doc-gen/catalogs.py`.", "",
             f"**{len(skills)} skills** · {modes['read-only']} read-only · "
             f"{modes['guarded-write']} guarded-write. "
             f"Verification labels: {levels['live']} live, {levels['partial']} partial, "
             f"{levels['shape-only']} shape-only.", "",
             "`partial` means selected reads have recorded live evidence; `shape-only` means "
             "command syntax was checked. Neither label certifies a complete workflow. "
             "Guarded-write describes recipes requiring a change plan and authorization; "
             "all bundled helper scripts and MCP tools remain read-only.", "",
             "Script counts include both shell entrypoints and Python helpers. Reference "
             "counts cover skill-local Markdown; shared resources are linked separately.", ""]
    for domain, names in DOMAINS.items():
        lines += [f"## {domain}", "", "| Skill | Purpose | Mode | Evidence | Scripts | Local refs | Shared resources |",
                  "|---|---|---|---|---:|---:|---|"]
        for name in names:
            s = skills[name]
            shared = ", ".join(f"[{ref}](../references/{ref})" for ref in s["shared"]) or "—"
            lines.append(f"| [{name}](../skills/{name}/SKILL.md) | {cell(s['purpose'])} | "
                         f"{s['mode']} | {s['verified']} | {s['scripts']} | {s['references']} | {shared} |")
        lines += [""]
    lines += ["## Choosing a skill", "", "The triggers below are copied from the shipped descriptions. "
              "Command samples are the first three read fences; define their variables using "
              "the skill's **Scope check** before running them. Outputs are bounded samples.", ""]
    for name, s in skills.items():
        lines += [f"<details><summary><strong>{name}</strong></summary>", "",
                  f"[Open skill](../skills/{name}/SKILL.md)", "",
                  f"**Use when:** {s['use']}", "", f"**Not for:** {s['exclude']}", ""]
        for command in s["commands"]:
            lines += ["```bash", command, "```", ""]
        lines += ["</details>", ""]
    return "\n".join(lines)


def readme_table(skills):
    lines = ["| Domain | Skill | Purpose |", "|---|---|---|"]
    for domain, names in DOMAINS.items():
        for i, name in enumerate(names):
            lines.append(f"| {domain if i == 0 else ''} | [{name}](skills/{name}/SKILL.md) | "
                         f"{cell(skills[name]['purpose'])} |")
    return "\n".join(lines)


async def mcp_markdown():
    sys.path.insert(0, str(ROOT / "runtime"))
    from oci_readonly.server import mcp

    tools = sorted(await mcp.list_tools(), key=lambda tool: tool.name)
    lines = ["# MCP tool reference", "", "[Documentation](README.md) · [Skills catalog](skills.md)", "",
             "Generated from the bundled server's `list_tools()` schemas without loading "
             "OCI credentials or making service calls. Regenerate with "
             "`uv run --frozen --project runtime python scripts/doc-gen/catalogs.py`.", "",
             f"**{len(tools)} tools**, all annotated read-only and non-destructive. "
             "`oci_price_lookup` uses public pricing; the other tools require OCI authentication. "
             "Annotations describe intent; fixed operation dispatch, explicit scope and "
             "IAM enforce the supported access.", "",
             "See [runtime configuration](../runtime/README.md) for authentication, scope, "
             "timeouts, pagination and output envelopes. No generic CLI, SQL or SDK executor is exposed.", "",
             "| Tool | Description | Read-only | Required arguments |", "|---|---|---|---|"]
    for tool in tools:
        required = tool.inputSchema.get("required", [])
        args = ", ".join(f"`{name}`" for name in required) or "None"
        lines.append(f"| [{tool.name}](#{tool.name.replace('_', '-')}) | "
                     f"{cell(tool.description or '')} | {str(tool.annotations.readOnlyHint).lower()} | {args} |")
    for tool in tools:
        schema = tool.inputSchema
        lines += ["", f"## {tool.name.replace('_', '-')}", "", f"`{tool.name}` — {tool.description}", "",
                  "| Argument | Type | Required | Default |", "|---|---|---|---|"]
        for name, prop in schema.get("properties", {}).items():
            kind = prop.get("type") or " / ".join(
                p.get("type", p.get("$ref", "object")) for p in prop.get("anyOf", [])) or "object"
            default = repr(prop["default"]) if "default" in prop else "—"
            lines.append(f"| `{name}` | {cell(kind)} | "
                         f"{'yes' if name in schema.get('required', []) else 'no'} | {cell(default)} |")
    return "\n".join(lines) + "\n"


def render():
    skills = load_skills()
    readme = (ROOT / "README.md").read_text()
    start, end = "<!-- skills:start -->", "<!-- skills:end -->"
    if readme.count(start) != 1 or readme.count(end) != 1:
        raise ValueError("README must contain one skills table marker pair")
    before, rest = readme.split(start)
    _, after = rest.split(end)
    return {
        "docs/skills.md": skills_markdown(skills),
        "docs/mcp-tools.md": asyncio.run(mcp_markdown()),
        "README.md": before + start + "\n" + readme_table(skills) + "\n" + end + after,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail on stale output without writing")
    args = parser.parse_args()
    stale = []
    for name, text in render().items():
        path = ROOT / name
        if not path.exists() or path.read_text() != text:
            stale.append(name)
            if not args.check:
                path.write_text(text)
    print(("Stale: " if args.check else "Updated: ") + ", ".join(stale) if stale else "Catalogs up to date")
    return int(args.check and bool(stale))


if __name__ == "__main__":
    raise SystemExit(main())
