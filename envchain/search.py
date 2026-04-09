"""Search and filter environment variables across profiles."""

from dataclasses import dataclass, field
from typing import Optional
import re


@dataclass
class SearchResult:
    """Represents a single search match."""
    profile_name: str
    var_name: str
    var_value: str
    matched_on: str  # 'name' or 'value'

    def __repr__(self) -> str:
        return (
            f"SearchResult(profile={self.profile_name!r}, "
            f"name={self.var_name!r}, matched_on={self.matched_on!r})"
        )


class EnvSearcher:
    """Search for environment variables across profiles."""

    def __init__(self, storage) -> None:
        self._storage = storage

    def search(
        self,
        query: str,
        profile_names: Optional[list] = None,
        search_values: bool = False,
        case_sensitive: bool = False,
        use_regex: bool = False,
    ) -> list:
        """Search for variables matching query across one or more profiles.

        Args:
            query: The search string or regex pattern.
            profile_names: Profiles to search; defaults to all profiles.
            search_values: Also search variable values if True.
            case_sensitive: Enable case-sensitive matching.
            use_regex: Treat query as a regular expression.

        Returns:
            List of SearchResult objects.
        """
        if not query:
            return []

        flags = 0 if case_sensitive else re.IGNORECASE

        if use_regex:
            try:
                pattern = re.compile(query, flags)
            except re.error as exc:
                raise ValueError(f"Invalid regex pattern: {exc}") from exc
            matcher = lambda text: bool(pattern.search(text))
        else:
            if not case_sensitive:
                q = query.lower()
                matcher = lambda text: q in text.lower()
            else:
                matcher = lambda text: query in text

        profiles = profile_names or self._storage.list_profiles()
        results = []

        for name in profiles:
            profile = self._storage.load_profile(name)
            if profile is None:
                continue
            for var_name, var_value in profile.variables.items():
                if matcher(var_name):
                    results.append(
                        SearchResult(name, var_name, var_value, matched_on="name")
                    )
                elif search_values and matcher(var_value):
                    results.append(
                        SearchResult(name, var_name, var_value, matched_on="value")
                    )

        return results
