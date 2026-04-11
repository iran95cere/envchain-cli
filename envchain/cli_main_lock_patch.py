"""Register 'lock' sub-commands into the main CLI parser."""
from __future__ import annotations

import argparse
import sys

from envchain.cli_lock import LockCommand


def register(subparsers: argparse._SubParsersAction, storage_dir: str) -> None:  # noqa: SLF001
    """Attach lock/unlock/status/list-locked to *subparsers*."""
    lock_p = subparsers.add_parser("lock", help="Lock a profile against writes")
    lock_p.add_argument("profile")
    lock_p.add_argument("--reason", default="", help="Optional reason for locking")

    unlock_p = subparsers.add_parser("unlock", help="Unlock a profile")
    unlock_p.add_argument("profile")

    status_p = subparsers.add_parser("lock-status", help="Show lock status of a profile")
    status_p.add_argument("profile")

    subparsers.add_parser("lock-list", help="List all locked profiles")


def _dispatch(args: argparse.Namespace, storage_dir: str) -> bool:
    """Handle lock-related commands.  Returns True if handled."""
    cmd = LockCommand(storage_dir)
    if args.command == "lock":
        cmd.lock(args.profile, reason=getattr(args, "reason", ""))
        return True
    if args.command == "unlock":
        cmd.unlock(args.profile)
        return True
    if args.command == "lock-status":
        cmd.status(args.profile)
        return True
    if args.command == "lock-list":
        cmd.list_locked()
        return True
    return False
