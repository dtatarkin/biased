#!/usr/bin/env python3
import argparse
import os

from dotenv import load_dotenv


def main():
    parser = argparse.ArgumentParser(
        description="Load environment variables from files and run a command.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example:\n  dotenv-run -f .env -f .env.local -- python manage.py runserver",
    )
    parser.add_argument(
        "-f",
        "--file",
        dest="files",
        action="append",
        default=[],
        help="Path to the .env file to load. Can be specified multiple times.",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command to execute, followed by its arguments.",
    )

    args = parser.parse_args()

    for f in args.files:
        load_dotenv(f, override=True)

    if args.command and args.command[0] == "--":
        cmd_args = args.command[1:]
    else:
        cmd_args = args.command

    if not cmd_args:
        parser.error("No command specified to execute.")

    os.execvp(cmd_args[0], cmd_args)  # nosec B606:start_process_with_no_shell


if __name__ == "__main__":
    main()
