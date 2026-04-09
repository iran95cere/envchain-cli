"""Main CLI entry point wiring all subcommands together."""

import argparse
import sys
from pathlib import Path

from envchain.storage import EnvStorage
from envchain.cli import EnvChainCLI
from envchain.cli_export import ExportCommand
from envchain.cli_import import ImportCommand
from envchain.cli_profile import ProfileCommand


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envchain",
        description="Manage encrypted per-project environment variable profiles.",
    )
    parser.add_argument(
        "--dir", default=".", help="Project directory (default: current directory)"
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("init", help="Initialize a new profile")
    set_p = sub.add_parser("set", help="Set a variable in the active profile")
    set_p.add_argument("key")
    set_p.add_argument("value")

    exp_p = sub.add_parser("export", help="Export profile variables")
    exp_p.add_argument("--format", default="bash")

    imp_p = sub.add_parser("import", help="Import variables from a file")
    imp_p.add_argument("file")
    imp_p.add_argument("--format", default=None)

    prof_p = sub.add_parser("profile", help="Profile management")
    prof_sub = prof_p.add_subparsers(dest="profile_cmd")
    prof_sub.add_parser("list")
    use_p = prof_sub.add_parser("use")
    use_p.add_argument("name")
    prof_sub.add_parser("current")
    prof_sub.add_parser("clear")

    return parser


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    project_dir = Path(args.dir).resolve()
    storage = EnvStorage(base_dir=str(project_dir))

    if args.command == "profile":
        cmd = ProfileCommand(storage=storage, project_dir=str(project_dir))
        if args.profile_cmd == "list":
            cmd.list_profiles()
        elif args.profile_cmd == "use":
            cmd.use_profile(args.name)
        elif args.profile_cmd == "current":
            cmd.current_profile()
        elif args.profile_cmd == "clear":
            cmd.clear_profile()
        else:
            parser.print_help()
    elif args.command is None:
        parser.print_help()
    else:
        print(f"Command '{args.command}' not yet wired in cli_main.", file=sys.stderr)


if __name__ == "__main__":
    main()
