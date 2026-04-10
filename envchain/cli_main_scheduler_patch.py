"""Argparse subcommand registration for the scheduler feature.

Call ``register(subparsers, storage_dir)`` from cli_main.build_parser to
attach the 'schedule' subcommand group.
"""

from __future__ import annotations

import time
from argparse import _SubParsersAction
from typing import Optional

from .cli_scheduler import SchedulerCommand


def register(subparsers: _SubParsersAction, storage_dir: str) -> None:
    p = subparsers.add_parser("schedule", help="Manage scheduled profile actions")
    sub = p.add_subparsers(dest="sched_cmd", required=True)

    # add
    p_add = sub.add_parser("add", help="Add a scheduled action")
    p_add.add_argument("profile", help="Profile name")
    p_add.add_argument(
        "action", choices=("activate", "deactivate", "expire"),
        help="Action to perform",
    )
    p_add.add_argument(
        "--at", type=float, default=None,
        help="Unix timestamp when to run (default: now + 60s)",
    )
    p_add.add_argument(
        "--repeat", type=int, default=None,
        metavar="SECONDS", help="Repeat interval in seconds",
    )

    # remove
    p_rm = sub.add_parser("remove", help="Remove a scheduled action")
    p_rm.add_argument("profile", help="Profile name")
    p_rm.add_argument("action", help="Action type")

    # list
    sub.add_parser("list", help="List all scheduled actions")

    # run-due
    sub.add_parser("run-due", help="Execute all actions that are due now")

    p.set_defaults(func=lambda args: _dispatch(args, storage_dir))


def _dispatch(args, storage_dir: str) -> None:
    cmd = SchedulerCommand(storage_dir)
    if args.sched_cmd == "add":
        run_at = args.at if args.at is not None else time.time() + 60
        cmd.add(args.profile, args.action, run_at, args.repeat)
    elif args.sched_cmd == "remove":
        cmd.remove(args.profile, args.action)
    elif args.sched_cmd == "list":
        cmd.list_actions()
    elif args.sched_cmd == "run-due":
        cmd.run_due()
