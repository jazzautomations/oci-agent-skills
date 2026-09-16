#!/usr/bin/env python3
"""Inventory the installed OCI CLI and SDK without credentials or service calls."""

import argparse
import importlib
import importlib.metadata
import inspect
import json
import pkgutil
import tempfile
from pathlib import Path
from catalog_rules import annotate


def load_cli():
    # Dynamic loader must initialize service import paths before importing cli_root.
    from oci_cli import dynamic_loader
    from oci_cli.cli_root import cli

    errors = []
    for service_dir in sorted(Path(dynamic_loader.services_dir).iterdir()):
        if service_dir.is_dir() and not service_dir.name.startswith("_"):
            try:
                dynamic_loader.load_service_dir(service_dir.name)
            except Exception as exc:
                errors.append({"module": service_dir.name, "error": type(exc).__name__})
    return cli, errors


def option_details(command):
    import click

    flags, required, boolean = [], [], []
    for parameter in command.params:
        if isinstance(parameter, click.Option):
            flags.extend(parameter.opts + parameter.secondary_opts)
            canonical = max(parameter.opts, key=len)
            if parameter.required or "[required]" in (parameter.help or "").lower():
                required.append(canonical)
            if parameter.is_flag:
                boolean.extend(parameter.opts + parameter.secondary_opts)
    return {
        "flags": sorted(flags),
        "required": sorted(required),
        "boolean_flags": sorted(boolean),
    }


def cli_inventory():
    import click

    root, errors = load_cli()
    commands, groups = [], []

    def walk(command, path):
        if isinstance(command, click.Group):
            groups.append(" ".join(path))
            for name, child in sorted(command.commands.items()):
                walk(child, path + [name])
        else:
            details = option_details(command)
            commands.append({"path": " ".join(path), **details,
                **annotate(" ".join(path)),
                "short_help": (command.short_help or (command.help or "").strip().split("\n")[0])[:180],
                **{"has_" + flag.replace("-", "_"): "--" + flag in details["flags"]
                   for flag in ("dry-run", "wait-for-state", "all", "force", "limit")}})

    walk(root, [])
    return {
        "schema_version": 2,
        "cli_version": importlib.metadata.version("oci-cli"),
        "sdk_version": importlib.metadata.version("oci"),
        "scope": "Installed Click command definitions including aliases; command leaves only. Required flags come from Click required or the CLI [required] help marker. No safety or authorization classification. Conditional requirements may exist in callbacks.",
        "root_command_count": len(root.commands),
        "group_count": len(groups) - 1,
        "command_count": len(commands),
        "global_options": option_details(root),
        "import_errors": errors,
        "commands": commands,
    }


def sdk_inventory():
    import oci

    packages, errors = [], []
    for info in sorted(pkgutil.iter_modules(oci.__path__), key=lambda item: item.name):
        if not info.ispkg or info.name.startswith("_"):
            continue
        try:
            module = importlib.import_module("oci." + info.name)
            clients = []
            for name, cls in inspect.getmembers(module, inspect.isclass):
                if name.endswith("Client") and cls.__module__.startswith(
                    "oci." + info.name + "."
                ):
                    operations = [
                        name
                        for name, value in cls.__dict__.items()
                        if not name.startswith("_") and inspect.isfunction(value)
                    ]
                    clients.append({"name": name, "operation_count": len(operations)})
            if clients:
                packages.append({"name": info.name, "clients": clients})
        except Exception as exc:
            errors.append({"module": "oci." + info.name, "error": type(exc).__name__})
    return {
        "schema_version": 2,
        "sdk_version": oci.__version__,
        "scope": "Installed OCI SDK packages exporting service *Client classes. Operation count is public functions defined directly on those classes; excludes __init__, private methods and CompositeOperations classes. Inventory only, not Oracle product coverage or a safety classification.",
        "package_count": len(packages),
        "client_count": sum(len(package["clients"]) for package in packages),
        "operation_count": sum(
            client["operation_count"]
            for package in packages
            for client in package["clients"]
        ),
        "import_errors": errors,
        "packages": packages,
    }


def write_cli(output, result, index=True):
    output.mkdir(parents=True, exist_ok=True)
    rows = result.pop("commands")
    # Inventory scope applies to both JSONL files through this shared sidecar.
    (output / "cli-meta.json").write_text(json.dumps(result, indent=2) + "\n")
    for filename, selected in [("cli.jsonl", rows), ("cli-read.jsonl", [r for r in rows if r["read_only"]])]:
        (output / filename).write_text("".join(json.dumps({"scope": result["scope"], "cli_version": result["cli_version"], **r}, ensure_ascii=True) + "\n" for r in selected))
    if index:
        from oci_cli.cli_root import cli
        services = []
        for name, command in sorted(cli.commands.items()):
            selected = [r for r in rows if r["path"].split()[0] == name]
            services.append({"name": name, "ops": len(selected),
                **{kind: sum(r["kind"] == kind for r in selected) for kind in ("read", "mutating", "destructive", "unknown")},
                "read_only": sum(r["read_only"] for r in selected),
                "purpose": (command.short_help or (command.help or "").strip().split("\n")[0])[:180]})
        (output / "index.json").write_text(json.dumps({**result, "services": services}, indent=2) + "\n")
    print(json.dumps({"commands": len(rows), "read_only": sum(r["read_only"] for r in rows), "import_errors": result["import_errors"]}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=Path(__file__).resolve().parents[1] / "catalog"
    )
    parser.add_argument("--format", choices=["jsonl"], default="jsonl")
    parser.add_argument("--index", action="store_true")
    parser.add_argument("--check", action="store_true", help="Regenerate in a temporary directory and compare shipped artifacts")
    parser.add_argument("--scripts", action="store_true", help="Generate script SHA256 registry and guard binding")
    parser.add_argument("--examples", action="store_true", help="Merge catalog/fragments/*.json")
    options = parser.parse_args()
    if options.scripts or options.examples:
        from inventory_artifacts import artifacts
        for name, content in artifacts(scripts=options.scripts, examples=options.examples).items():
            path = options.output / name
            if options.check:
                if not path.is_file() or path.read_text() != content:
                    raise SystemExit("Catalog differs: " + name)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
        print("Script/example artifacts verified." if options.check else "Script/example artifacts generated.")
        return
    result = cli_inventory()
    if result["cli_version"] != "3.93.0":
        raise SystemExit("Catalog requires OCI CLI 3.93.0")
    if options.check:
        with tempfile.TemporaryDirectory() as directory:
            generated = Path(directory)
            write_cli(generated, result, options.index)
            for path in generated.iterdir():
                if not (options.output / path.name).is_file() or path.read_bytes() != (options.output / path.name).read_bytes():
                    raise SystemExit("Catalog differs: " + path.name)
        print("Catalog regeneration is byte-identical.")
    else:
        write_cli(options.output, result, options.index)


if __name__ == "__main__":
    main()
