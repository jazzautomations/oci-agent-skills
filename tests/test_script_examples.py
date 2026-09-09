import importlib.util
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import click
import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location(
    "check_examples", SCRIPTS / "check_examples.py"
)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


@pytest.fixture
def cli():
    root = click.Group("oci")
    compute = click.Group("compute")
    instance = click.Group("shape")
    root.add_command(compute)
    compute.add_command(instance)
    instance.add_command(
        click.Command(
            "list",
            params=[
                click.Option(["--compartment-id"], help="Compartment [required]"),
                click.Option(["--limit"], type=int),
                click.Option(["--all"], is_flag=True),
                click.Option(["--from-json"]),
            ],
            callback=lambda **kwargs: pytest.fail("Command must never execute offline"),
        )
    )
    return root


def example(*extra):
    return {
        "id": "compute-list",
        "skill": "oci-compute",
        "argv": [
            "compute",
            "shape",
            "list",
            "--compartment-id",
            "${COMPARTMENT_ID}",
            *extra,
        ],
    }


def test_validates_help_without_executing_callback(cli):
    path, values, _ = checker.validate_example(example("--limit", "10"), cli)
    assert path == "compute shape list"
    assert values["--limit"] == "10"


@pytest.mark.parametrize(
    "argv",
    [
        ["compute", "shape", "missing"],
        ["compute", "shape", "list"],
        ["compute", "shape", "list", "--compartment-id"],
        ["compute", "shape", "list", "--compartment-id", "${SECRET}"],
        ["compute", "shape", "list", "--compartment-id", "x", "--unknown", "y"],
        [
            "compute",
            "shape",
            "list",
            "--compartment-id",
            "x",
            "--limit",
            "1",
            "--limit",
            "2",
        ],
    ],
)
def test_rejects_invalid_paths_options_and_placeholders(cli, argv):
    with pytest.raises(ValueError):
        checker.validate_example({"id": "example", "argv": argv}, cli)


@pytest.mark.parametrize("extra", [("--all",), ("--from-json", "file://private")])
def test_live_rejects_unbounded_and_local_file_options(cli, extra):
    record = example(*extra)
    path, values, options = checker.validate_example(record, cli)
    with pytest.raises(ValueError):
        checker.live_argv(record, path, values, options, {"COMPARTMENT_ID": "example"})


def test_live_binds_scope_and_forces_single_page(cli):
    record = example("--limit", "500")
    path, values, options = checker.validate_example(record, cli)
    argv = checker.live_argv(
        record, path, values, options, {"COMPARTMENT_ID": "configured"}
    )
    assert argv[-1] == "1"
    assert "configured" in argv
    values["--compartment-id"] = "unconfigured"
    with pytest.raises(ValueError):
        checker.live_argv(record, path, values, options, {})


def test_live_rejects_non_allowlisted_path():
    with pytest.raises(ValueError):
        checker.live_argv(
            {"argv": ["compute", "shape", "terminate"]},
            "compute instance terminate",
            {},
            {},
            {},
        )


def test_live_error_output_is_suppressed(monkeypatch):
    process = SimpleNamespace(
        returncode=1, stdout="secret", stderr="private key secret"
    )
    monkeypatch.setattr(checker.subprocess, "run", lambda *args, **kwargs: process)
    result = checker.run_live(
        ["compute", "shape", "list"], "DEFAULT", "us-chicago-1"
    )
    assert result == {"status": "failed", "exit_code": 1}


def test_live_timeout_no_shell_and_only_counts(monkeypatch):
    def run(command, **kwargs):
        assert kwargs["timeout"] == 30
        assert not kwargs.get("shell")
        assert "--no-retry" in command
        assert "OCI_CLI_AUTO_PROMPT" not in kwargs["env"]
        assert command[command.index("--output") + 1] == "json"
        return SimpleNamespace(returncode=0, stdout='{"data":[{"name":"private"}]}')

    monkeypatch.setattr(checker.subprocess, "run", run)
    assert checker.run_live(["compute", "shape", "list"], "DEFAULT", "us-chicago-1") == {
        "status": "passed",
        "count": 1,
        "truncated": False,
    }


def test_live_timeout_is_structured(monkeypatch):
    def run(*args, **kwargs):
        raise subprocess.TimeoutExpired("private", 30, output="secret")

    monkeypatch.setattr(checker.subprocess, "run", run)
    assert checker.run_live(["compute", "shape", "list"], "DEFAULT", "us-chicago-1") == {"status": "timeout"}


def test_cli_empty_list_render_is_success(monkeypatch):
    process = SimpleNamespace(returncode=0, stdout="", stderr="")
    monkeypatch.setattr(checker.subprocess, "run", lambda *args, **kwargs: process)
    result = checker.run_live(["compute", "shape", "list"], "DEFAULT", "us-chicago-1")
    assert result["status"] == "passed"
    assert result["count"] == 0
    assert result["output_kind"] == "empty_cli_response"


def test_global_options_are_validated_without_callbacks(cli):
    cli.params.append(click.Option(['--profile']))
    record = example('--profile', '${PROFILE}')
    path, values, _ = checker.validate_example(record, cli)
    assert path == 'compute shape list'
    assert values['--profile'] == '${PROFILE}'
    # Offline recognition grants no live authorization.
    with pytest.raises(ValueError):
        checker.live_argv(record, path, values, {}, {'PROFILE': 'DEFAULT'})
