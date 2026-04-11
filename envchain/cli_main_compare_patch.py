"""Registers the 'compare' subcommand into the main CLI parser."""
import argparse
from typing import Any


def register(subparsers: Any, storage_factory) -> None:
    """Add the compare subcommand to an existing subparsers group."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "compare",
        help="Compare environment variables between two profiles",
    )
    parser.add_argument("left", help="Left (base) profile name")
    parser.add_argument("right", help="Right (target) profile name")
    parser.add_argument(
        "--password", "-p", default=None, help="Shared decryption password"
    )
    parser.add_argument(
        "--show-same",
        action="store_true",
        default=False,
        help="Also display keys that are identical in both profiles",
    )
    parser.add_argument(
        "--unmask",
        action="store_true",
        default=False,
        help="Show actual values instead of masking them",
    )
    parser.set_defaults(func=_dispatch)


def _dispatch(args: argparse.Namespace, storage_factory) -> None:
    """Dispatch parsed arguments to CompareCommand."""
    from envchain.cli_compare import CompareCommand
    import getpass

    storage = storage_factory()
    password = args.password
    if password is None:
        try:
            password = getpass.getpass("Password: ")
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            raise SystemExit(1)

    cmd = CompareCommand(storage)
    cmd.run(
        left=args.left,
        right=args.right,
        password=password,
        show_same=args.show_same,
        mask_values=not args.unmask,
    )
