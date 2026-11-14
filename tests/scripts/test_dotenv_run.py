import os
import subprocess
import sys
from pathlib import Path

import pytest

_PRINT_ENV = (
    "import os, sys; print(*(os.environ.get(k, '<unset>') for k in sys.argv[1:]))"
)


def _run(
    *args: str, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "biased.scripts.dotenv_run", *args],
        capture_output=True,
        text=True,
        env={**os.environ, **(env or {})},
        check=False,
    )


def _print_env(*keys: str) -> list[str]:
    return [sys.executable, "-c", _PRINT_ENV, *keys]


@pytest.fixture
def base_env(tmp_path: Path) -> Path:
    path = tmp_path / "base.env"
    path.write_text("FOO=base\nBAR=base\nSHELL_SET=file\n")
    return path


@pytest.fixture
def local_env(tmp_path: Path) -> Path:
    path = tmp_path / "local.env"
    path.write_text("BAR=local\nREF=${SHELL_SET}-${FOO}\n")
    return path


def test_later_file_overrides_earlier(base_env: Path, local_env: Path) -> None:
    result = _run(
        "-f", str(base_env), "-f", str(local_env), "--", *_print_env("FOO", "BAR")
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.split() == ["base", "local"]


def test_calling_environment_overrides_files(base_env: Path, local_env: Path) -> None:
    result = _run(
        "-f",
        str(base_env),
        "-f",
        str(local_env),
        "--",
        *_print_env("SHELL_SET", "REF"),
        env={"SHELL_SET": "shell"},
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.split() == ["shell", "shell-base"]


def test_separator_is_optional(base_env: Path) -> None:
    result = _run("-f", str(base_env), *_print_env("FOO"))

    assert result.returncode == 0, result.stderr
    assert result.stdout.split() == ["base"]


def test_command_options_pass_through(base_env: Path) -> None:
    script = "import sys; print(sys.argv[1:])"
    result = _run(
        "-f", str(base_env), "--", sys.executable, "-c", script, "-f", "--", "x"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "['-f', '--', 'x']"


def test_missing_env_file_is_a_usage_error(tmp_path: Path) -> None:
    result = _run("-f", str(tmp_path / "absent.env"), "--", "true")

    assert result.returncode == 2
    assert "env file not found" in result.stderr


def test_no_command_is_a_usage_error(base_env: Path) -> None:
    result = _run("-f", str(base_env), "--")

    assert result.returncode == 2
    assert "no command specified" in result.stderr


def test_unknown_command_exits_127() -> None:
    result = _run("--", "dotenv-run-no-such-command")

    assert result.returncode == 127
    assert (
        result.stderr == "dotenv-run: dotenv-run-no-such-command: command not found\n"
    )


def test_non_executable_command_exits_126(tmp_path: Path) -> None:
    script = tmp_path / "script.sh"
    script.write_text("#!/bin/sh\n")

    result = _run("--", str(script))

    assert result.returncode == 126
    assert result.stderr == f"dotenv-run: {script}: Permission denied\n"
