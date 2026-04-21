"""CLI command for swapping environment variable values within a profile."""
import sys
from envchain.env_swap import EnvSwapper


class SwapCommand:
    def __init__(self, storage):
        self._storage = storage
        self._swapper = EnvSwapper()

    def run(self, profile: str, var_a: str, var_b: str, password: str) -> None:
        """Swap the values of var_a and var_b in the given profile."""
        profile_obj = self._storage.load_profile(profile, password)
        if profile_obj is None:
            print(f"[error] Profile {profile!r} not found.", file=sys.stderr)
            sys.exit(1)

        vars_dict = dict(profile_obj.vars)
        result = self._swapper.swap(vars_dict, var_a, var_b)

        if not result.success:
            print(f"[error] {result.error}", file=sys.stderr)
            sys.exit(1)

        profile_obj.vars = vars_dict
        self._storage.save_profile(profile_obj, password)
        print(
            f"[ok] Swapped {var_a!r} ({result.value_a!r}) "
            f"<-> {var_b!r} ({result.value_b!r}) in profile {profile!r}."
        )

    def bulk_run(
        self, profile: str, pairs: list, password: str
    ) -> None:
        """Swap multiple variable pairs in one pass."""
        profile_obj = self._storage.load_profile(profile, password)
        if profile_obj is None:
            print(f"[error] Profile {profile!r} not found.", file=sys.stderr)
            sys.exit(1)

        vars_dict = dict(profile_obj.vars)
        report = self._swapper.swap_many(vars_dict, pairs)

        if report.has_failures:
            for r in report.results:
                if not r.success:
                    print(f"[error] {r.error}", file=sys.stderr)
            sys.exit(1)

        profile_obj.vars = vars_dict
        self._storage.save_profile(profile_obj, password)
        print(
            f"[ok] {report.success_count} swap(s) applied to profile {profile!r}."
        )
