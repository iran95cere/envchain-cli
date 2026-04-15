"""CLI command for encoding/decoding environment variable values."""
from __future__ import annotations

import sys
from typing import Optional

from envchain.env_encode import EncodeFormat, EnvEncoder


class EncodeCommand:
    """Encode or decode variable values in a profile."""

    def __init__(self, storage):
        self._storage = storage
        self._encoder = EnvEncoder()

    def run(
        self,
        profile_name: str,
        fmt: str,
        decode: bool = False,
        dry_run: bool = False,
    ) -> None:
        try:
            enc_fmt = EncodeFormat(fmt)
        except ValueError:
            print(
                f"Unknown format '{fmt}'. Available: {', '.join(EnvEncoder.FORMATS)}",
                file=sys.stderr,
            )
            sys.exit(1)

        profile = self._storage.load_profile(profile_name)
        if profile is None:
            print(f"Profile '{profile_name}' not found.", file=sys.stderr)
            sys.exit(1)

        vars_ = dict(profile.variables)
        if decode:
            report = self._encoder.decode(vars_, enc_fmt)
            action = "Decoded"
        else:
            report = self._encoder.encode(vars_, enc_fmt)
            action = "Encoded"

        for result in report.results:
            if result.changed:
                print(f"  {result.name}: {result.original!r} -> {result.encoded!r}")

        if not report.has_changes:
            print("No values changed.")
            return

        if dry_run:
            print(f"[dry-run] {action} {report.encoded_count} variable(s).")
            return

        for result in report.results:
            profile.variables[result.name] = result.encoded

        self._storage.save_profile(profile)
        print(f"{action} {report.encoded_count} variable(s) in '{profile_name}'.")

    def list_formats(self) -> None:
        print("Available encode formats:")
        for fmt in EnvEncoder.FORMATS:
            print(f"  {fmt}")
