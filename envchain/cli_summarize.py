"""CLI command for summarizing environment profiles."""
from envchain.env_summarize import EnvSummarizer


class SummarizeCommand:
    def __init__(self, storage):
        self.storage = storage
        self.summarizer = EnvSummarizer()

    def run(self, profile_names=None):
        available = self.storage.list_profiles()
        if not available:
            print("No profiles found.")
            return

        targets = profile_names if profile_names else available
        profiles = {}
        for name in targets:
            profile = self.storage.load_profile(name)
            if profile is None:
                print(f"Warning: profile '{name}' not found, skipping.")
                continue
            profiles[name] = profile.variables if hasattr(profile, "variables") else {}

        if not profiles:
            print("No valid profiles to summarize.")
            return

        report = self.summarizer.summarize_all(profiles)
        self._display(report)

    def _display(self, report):
        print(f"Summary: {report.profile_count} profile(s), {report.total_vars} total variable(s)")
        print()
        for entry in report.entries:
            print(f"  Profile : {entry.profile}")
            print(f"    Variables  : {entry.total_vars}")
            print(f"    Empty      : {entry.empty_vars}")
            print(f"    Longest key: {entry.longest_key or '(none)'}")
            print(f"    Max val len: {entry.longest_value_len}")
            print()
