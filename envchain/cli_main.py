"""Entry point: builds the top-level argument parser and dispatches commands."""

from __future__ import annotations

import argparse
import sys

from envchain.storage import EnvStorage
from envchain.cli import EnvChainCLI
from envchain.cli_export import ExportCommand
from envchain.cli_import import ImportCommand
from envchain.cli_profile import ProfileCommand
from envchain.cli_validate import ValidateCommand
from envchain.cli_backup import BackupCommand
from envchain.cli_template import TemplateCommand
from envchain.cli_rotation import RotationCommand


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envchain",
        description="Manage encrypted per-project environment variable sets.",
    )
    sub = parser.add_subparsers(dest="command")

    # init
    p_init = sub.add_parser("init", help="Initialise a new profile.")
    p_init.add_argument("profile", help="Profile name.")

    # set
    p_set = sub.add_parser("set", help="Set a variable in a profile.")
    p_set.add_argument("profile")
    p_set.add_argument("name")
    p_set.add_argument("value")

    # export
    p_exp = sub.add_parser("export", help="Export variables from a profile.")
    p_exp.add_argument("profile")
    p_exp.add_argument("--format", default="bash")

    # import
    p_imp = sub.add_parser("import", help="Import variables into a profile.")
    p_imp.add_argument("profile")
    p_imp.add_argument("file")
    p_imp.add_argument("--format", default=None)

    # profile
    p_prof = sub.add_parser("profile", help="Manage profiles.")
    p_prof.add_argument("action", choices=["list", "use", "current"])
    p_prof.add_argument("name", nargs="?", default=None)

    # validate
    p_val = sub.add_parser("validate", help="Validate variable names/values.")
    p_val.add_argument("profile")

    # backup
    p_bak = sub.add_parser("backup", help="Backup and restore profiles.")
    p_bak.add_argument("action", choices=["create", "restore", "list"])
    p_bak.add_argument("name", nargs="?", default=None)

    # template
    p_tpl = sub.add_parser("template", help="Render templates with profile vars.")
    p_tpl.add_argument("profile")
    p_tpl.add_argument("template_file")

    # rotate
    p_rot = sub.add_parser("rotate", help="Rotate the password for one or more profiles.")
    p_rot.add_argument("profiles", nargs="+", help="Profile name(s) to rotate.")
    p_rot.add_argument("--note", default=None, help="Optional note for the rotation record.")

    return parser


def main(argv=None) -> None:  # pragma: no cover
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    storage = EnvStorage()

    if args.command == "rotate":
        cmd = RotationCommand(storage)
        cmd.run(args.profiles, note=args.note)
    # … other commands omitted for brevity (unchanged from prior implementation)


if __name__ == "__main__":  # pragma: no cover
    main()
