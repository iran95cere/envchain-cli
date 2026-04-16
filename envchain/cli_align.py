"""CLI command for aligning environment variable values."""
from __future__ import annotations
import sys
from envchain.env_align import EnvAligner


class AlignCommand:
    def __init__(self, storage, profile_name: str, pad_width: int = 0):
        self.storage = storage
        self.profile_name = profile_name
        self.pad_width = pad_width

    def run(self, dry_run: bool = False) -> None:
        profile = self.storage.load_profile(self.profile_name)
        if profile is None:
            print(f"Profile '{self.profile_name}' not found.", file=sys.stderr)
            sys.exit(1)

        aligner = EnvAligner(pad_width=self.pad_width)
        report = aligner.align(dict(profile.variables))

        if not report.has_changes:
            print("No alignment changes needed.")
            return

        for result in report.results:
            if result.changed:
                print(f"  {result.name}: {result.original!r} -> {result.aligned!r}")

        if dry_run:
            print(f"Dry run: {report.changed_count} variable(s) would be aligned.")
            return

        profile.update_vars(report.aligned_vars())
        self.storage.save_profile(profile)
        print(f"Aligned {report.changed_count} variable(s) in '{self.profile_name}'.")

    def show_report(self) -> None:
        profile = self.storage.load_profile(self.profile_name)
        if profile is None:
            print(f"Profile '{self.profile_name}' not found.", file=sys.stderr)
            sys.exit(1)

        aligner = EnvAligner(pad_width=self.pad_width)
        report = aligner.align(dict(profile.variables))
        print(repr(report))
        for result in report.results:
            print(f"  {result}")
