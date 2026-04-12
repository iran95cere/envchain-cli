"""Register 'notify' subcommands into the main CLI parser."""
from __future__ import annotations

import argparse
from typing import Optional

from envchain.env_notify import NotificationBus
from envchain.cli_notify import NotifyCommand

# Module-level shared bus (can be replaced in tests)
_default_bus = NotificationBus()


def register(subparsers: argparse._SubParsersAction,
             bus: Optional[NotificationBus] = None) -> None:
    b = bus or _default_bus
    cmd = NotifyCommand(b)

    notify_p = subparsers.add_parser("notify", help="Manage notifications")
    notify_sub = notify_p.add_subparsers(dest="notify_cmd")

    hist_p = notify_sub.add_parser("history", help="Show notification history")
    hist_p.add_argument("--profile", default=None, help="Filter by profile name")
    hist_p.set_defaults(func=lambda args: cmd.show_history(profile=args.profile))

    clear_p = notify_sub.add_parser("clear", help="Clear notification history")
    clear_p.set_defaults(func=lambda args: cmd.clear())

    send_p = notify_sub.add_parser("send", help="Send a notification")
    send_p.add_argument("message", help="Notification message")
    send_p.add_argument("--level", default="info", help="Level: info, warning, error")
    send_p.add_argument("--profile", default=None, help="Associated profile")
    send_p.set_defaults(
        func=lambda args: cmd.send(args.message, level=args.level, profile=args.profile)
    )

    count_p = notify_sub.add_parser("count", help="Count notifications")
    count_p.add_argument("--profile", default=None, help="Filter by profile")
    count_p.set_defaults(func=lambda args: cmd.count(profile=args.profile))

    notify_p.set_defaults(func=lambda args: _dispatch(args, notify_p))


def _dispatch(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if not getattr(args, "notify_cmd", None):
        parser.print_help()
    else:
        args.func(args)
