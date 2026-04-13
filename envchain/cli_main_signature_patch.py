"""Register 'signature' sub-commands into the main CLI parser."""
from __future__ import annotations

import sys
from typing import Any


def register(subparsers: Any) -> None:
    """Attach the 'signature' command group to *subparsers*."""
    sig_parser = subparsers.add_parser(
        "signature", help="Sign and verify profile integrity"
    )
    sig_sub = sig_parser.add_subparsers(dest="sig_cmd")

    sign_p = sig_sub.add_parser("sign", help="Sign a profile")
    sign_p.add_argument("profile", help="Profile name")

    verify_p = sig_sub.add_parser("verify", help="Verify a profile signature")
    verify_p.add_argument("profile", help="Profile name")

    remove_p = sig_sub.add_parser("remove", help="Remove a profile signature")
    remove_p.add_argument("profile", help="Profile name")

    sig_sub.add_parser("list", help="List signed profiles")


def _dispatch(args: Any, storage: Any) -> None:
    """Dispatch parsed *args* to the appropriate SignatureCommand method."""
    from envchain.cli_signature import SignatureCommand

    cmd = SignatureCommand(storage)

    sig_cmd = getattr(args, "sig_cmd", None)
    if sig_cmd == "sign":
        cmd.sign(args.profile)
    elif sig_cmd == "verify":
        cmd.verify(args.profile)
    elif sig_cmd == "remove":
        cmd.remove(args.profile)
    elif sig_cmd == "list":
        cmd.list_signed()
    else:
        print("Usage: envchain signature <sign|verify|remove|list> [profile]", file=sys.stderr)
        sys.exit(1)
