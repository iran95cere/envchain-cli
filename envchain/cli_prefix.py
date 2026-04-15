"""CLI command for adding/removing variable name prefixes."""
import sys
from envchain.env_prefix import EnvPrefixer


class PrefixCommand:
    def __init__(self, storage):
        self._storage = storage
        self._prefixer = EnvPrefixer()

    def run(self, profile_name: str, prefix: str, mode: str, password: str, dry_run: bool = False) -> None:
        """Add or remove a prefix from variable names in a profile.

        Args:
            profile_name: Name of the profile to modify.
            prefix: The prefix string to add or remove.
            mode: Either 'add' or 'remove'.
            password: Decryption password for the profile.
            dry_run: If True, print changes without saving.
        """
        if mode not in ("add", "remove"):
            print(f"[error] mode must be 'add' or 'remove', got {mode!r}", file=sys.stderr)
            sys.exit(1)

        profile = self._storage.load_profile(profile_name, password)
        if profile is None:
            print(f"[error] profile {profile_name!r} not found", file=sys.stderr)
            sys.exit(1)

        vars_ = dict(profile.variables)

        if mode == "add":
            report = self._prefixer.add_prefix(vars_, prefix)
        else:
            report = self._prefixer.remove_prefix(vars_, prefix)

        if not report.has_changes:
            print("No changes.")
            return

        for r in report.results:
            if r.changed:
                print(f"  {r.original!r} -> {r.transformed!r}")

        if dry_run:
            print(f"[dry-run] {report.changed_count} variable(s) would be renamed.")
            return

        new_vars = self._prefixer.apply(vars_, report)
        profile.variables = new_vars
        self._storage.save_profile(profile, password)
        print(f"Renamed {report.changed_count} variable(s) in profile {profile_name!r}.")

    def show_report(self, profile_name: str, prefix: str, mode: str, password: str) -> None:
        """Print a preview of prefix changes without applying them."""
        self.run(profile_name, prefix, mode, password, dry_run=True)
