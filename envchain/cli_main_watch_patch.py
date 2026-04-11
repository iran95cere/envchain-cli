"""Patch cli_main to register the 'watch' sub-command."""
from __future__ import annotations

import argparse
import sys

from envchain.cli_watch import WatchCommand


def register(subparsers: argparse._SubParsersAction, storage_dir: str) -> None:
    """Add the 'watch' parser to an existing subparsers group."""
    p = subparsers.add_parser(
        "watch",
        help="Monitor profile files for changes",
    )
    p.add_argument(
        "--profile",
        metavar="NAME",
        default=None,
        help="Filter events to a single profile",
    )
    p.add_argument(
        "--interval",
        type=float,
        default=1.0,
        metavar="SECONDS",
        help="Polling interval in seconds (default: 1.0)",
    )
    p.add_argument(
        "--status",
        action="store_true",
        help="Print a one-shot status snapshot and exit",
    )
    p.set_defaults(_storage_dir=storage_dir)


def _dispatch(args: argparse.Namespace) -> None:
    """Dispatch a parsed 'watch' namespace to WatchCommand."""
    cmd = WatchCommand(
        storage_dir=args._storage_dir,
        poll_interval=args.interval,
    )
    if args.status:
        cmd.show_status()
        return
    cmd.run(profile_filter=args.profile)
