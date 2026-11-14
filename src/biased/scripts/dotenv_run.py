"""Run a command with variables loaded from one or more dotenv files.

`python-dotenv`'s own `dotenv run` takes a single file; this layers several.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import NoReturn

from dotenv import load_dotenv

_EXIT_NOT_EXECUTABLE = 126
_EXIT_NOT_FOUND = 127


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("no command specified to execute")

    missing = [path for path in args.files if not Path(path).is_file()]
    if missing:
        parser.error(f"env file not found: {', '.join(missing)}")

    _load_layered(args.files)
    _exec(command)


def _build_parser() -> argparse.ArgumentParser:
    # argparse rather than typer: REMAINDER hands the wrapped command's own
    # options through untouched, and typer would add a dependency to every
    # consumer of biased for one small script.
    parser = argparse.ArgumentParser(
        prog="dotenv-run",
        description=(
            "Load environment variables from files and run a command. "
            "A later file overrides an earlier one; a variable already set in "
            "the calling environment overrides them all."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example:\n  dotenv-run -f .env -f .env.local -- python manage.py runserver",
    )
    parser.add_argument(
        "-f",
        "--file",
        dest="files",
        action="append",
        default=[],
        help="Path to a .env file to load. Can be specified multiple times.",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command to execute, followed by its arguments.",
    )
    return parser


def _load_layered(files: list[str]) -> None:
    # override=True lets a later file replace an earlier one; restoring the
    # calling environment after each file keeps it on top, and lets the next
    # file's ${VAR} references see the value the command will finally get.
    calling_env = dict(os.environ)
    for path in files:
        load_dotenv(path, override=True)
        os.environ.update(calling_env)


def _exec(command: list[str]) -> NoReturn:
    try:
        # Replacing this process with the caller's own command is the script's purpose.
        os.execvp(command[0], command)  # nosec B606:start_process_with_no_shell  # noqa: S606
    except FileNotFoundError:
        _fail(f"{command[0]}: command not found", _EXIT_NOT_FOUND)
    except OSError as exc:
        _fail(f"{command[0]}: {exc.strerror}", _EXIT_NOT_EXECUTABLE)


def _fail(message: str, code: int) -> NoReturn:
    print(f"dotenv-run: {message}", file=sys.stderr)
    sys.exit(code)


if __name__ == "__main__":
    main()
