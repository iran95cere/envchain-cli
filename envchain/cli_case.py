"""CLI command for converting environment variable name/value casing."""
import sys
from envchain.env_case import EnvCaseConverter, CaseStyle


class CaseCommand:
    """Handles the 'case' subcommand for envchain-cli."""

    VALID_TARGETS = ("name", "value")

    def __init__(self, storage):
        self.storage = storage
        self.converter = EnvCaseConverter()

    def run(self, profile_name: str, style: str, target: str = "name", dry_run: bool = False) -> None:
        try:
            style_enum = CaseStyle(style)
        except ValueError:
            valid = ", ".join(s.value for s in CaseStyle)
            print(f"[error] Unknown style '{style}'. Valid options: {valid}", file=sys.stderr)
            sys.exit(1)

        if target not in self.VALID_TARGETS:
            print(f"[error] Invalid target '{target}'. Use 'name' or 'value'.", file=sys.stderr)
            sys.exit(1)

        profile = self.storage.load_profile(profile_name)
        if profile is None:
            print(f"[error] Profile '{profile_name}' not found.", file=sys.stderr)
            sys.exit(1)

        report = self.converter.convert_vars(profile.vars, style_enum, target=target)

        if not report.has_changes:
            print(f"No changes needed for profile '{profile_name}'.")
            return

        for result in report.results:
            if result.changed:
                print(f"  {result.original!r} -> {result.converted!r}")

        if dry_run:
            print(f"[dry-run] {report.changed_count} change(s) would be applied.")
            return

        if target == "name":
            new_vars = {}
            for r in report.results:
                new_vars[r.converted] = profile.vars[r.name]
            profile.vars = new_vars
        else:
            for r in report.results:
                if r.changed:
                    profile.vars[r.name] = r.converted

        self.storage.save_profile(profile_name, profile)
        print(f"Applied {report.changed_count} case conversion(s) to '{profile_name}'.")

    def list_styles(self) -> None:
        print("Available case styles:")
        for style in CaseStyle:
            print(f"  {style.value}")
