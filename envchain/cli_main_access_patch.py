"""Patch to register 'access' sub-commands in the main CLI parser."""
from __future__ import annotations

import argparse
import sys
from typing import Optional

from envchain.cli_access import AccessCommand


def register(subparsers: argparse._SubParsersAction, storage_dir: str) -> None:
    """Attach 'access' sub-command to *subparsers*."""
    p = subparsers.add_parser("access", help="Manage profile access control rules")
    sub = p.add_subparsers(dest="access_cmd")

    # add
    p_add = sub.add_parser("add", help="Add or update an access rule")
    p_add.add_argument("profile")
    p_add.add_argument("--allow", dest="allowed", nargs="*", default=[], metavar="USER")
    p_add.add_argument("--deny", dest="denied", nargs="*", default=[], metavar="USER")
    p_add.add_argument("--read-only", action="store_true", default=False)

    # remove
    p_rm = sub.add_parser("remove", help="Remove an access rule")
    p_rm.add_argument("profile")

    # check
    p_chk = sub.add_parser("check", help="Check access for a user")
    p_chk.add_argument("profile")
    p_chk.add_argument("user")
    p_chk.add_argument("--write", action="store_true", default=False)

    # list
    sub.add_parser("list", help="List all access rules")

    p.set_defaults(_access_storage=storage_dir)


def _dispatch(args: argparse.Namespace) -> None:
    """Dispatch parsed *args* to the appropriate AccessCommand method."""
    cmd = AccessCommand(args._access_storage)
    if args.access_cmd == "add":
        cmd.add(args.profile, args.allowed, args.denied, args.read_only)
    elif args.access_cmd == "remove":
        cmd.remove(args.profile)
    elif args.access_cmd == "check":
        cmd.check(args.profile, args.user, write=args.write)
    elif args.access_cmd == "list":
        cmd.list_rules()
    else:
        print("Usage: envchain access {add,remove,check,list} ...")
        sys.exit(1)
