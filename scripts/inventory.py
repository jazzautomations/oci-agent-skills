#!/usr/bin/env python3
"""Inventory the installed OCI CLI and SDK without credentials or service calls."""

import argparse
import importlib
import importlib.metadata
import inspect
import json
import pkgutil
from pathlib import Path


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
            commands.append({"path": " ".join(path), **option_details(command)})

    walk(root, [])
    return {
        "schema_version": 1,
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
        "schema_version": 1,
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=Path(__file__).resolve().parents[1] / "catalog"
    )
    options = parser.parse_args()
    options.output.mkdir(parents=True, exist_ok=True)
    for name, build in [("cli", cli_inventory), ("sdk", sdk_inventory)]:
        result = build()
        (options.output / f"{name}.json").write_text(
            json.dumps(result, separators=(",", ":"), ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(
            json.dumps(
                {
                    "catalog": name,
                    **{
                        key: value
                        for key, value in result.items()
                        if key.endswith("_count") or key.endswith("_version")
                    },
                    "import_errors": len(result["import_errors"]),
                }
            )
        )


if __name__ == "__main__":
    main()
