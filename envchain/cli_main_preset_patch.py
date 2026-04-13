"""Patch to register 'preset' sub-commands into cli_main's argument parser."""
from __future__ import annotations

import argparse
import sys


def register(subparsers: argparse._SubParsersAction) -> None:
    """Attach preset sub-commands to an existing subparsers group."""
    preset_p = subparsers.add_parser("preset", help="Manage env var presets")
    preset_sub = preset_p.add_subparsers(dest="preset_cmd")

    # add
    add_p = preset_sub.add_parser("add", help="Define a new preset")
    add_p.add_argument("name", help="Preset name")
    add_p.add_argument("--description", "-d", default="", help="Short description")
    add_p.add_argument("vars", nargs="*", metavar="KEY=VALUE", help="Variable defaults")

    # remove
    rm_p = preset_sub.add_parser("remove", help="Delete a preset")
    rm_p.add_argument("name", help="Preset name")

    # list
    preset_sub.add_parser("list", help="List all presets")

    # show
    show_p = preset_sub.add_parser("show", help="Show preset details")
    show_p.add_argument("name", help="Preset name")


def _dispatch(args: argparse.Namespace, storage_dir: str) -> None:
    """Dispatch parsed args to the appropriate PresetCommand method."""
    from envchain.env_preset import PresetManager
    from envchain.cli_preset import PresetCommand

    mgr = PresetManager(storage_dir)
    cmd = PresetCommand(mgr)

    sub = getattr(args, "preset_cmd", None)
    if sub == "add":
        cmd.add(args.name, args.description, args.vars or [])
    elif sub == "remove":
        cmd.remove(args.name)
    elif sub == "list":
        cmd.list_presets()
    elif sub == "show":
        cmd.show(args.name)
    else:
        print("Usage: envchain preset {add,remove,list,show}", file=sys.stderr)
        sys.exit(1)
