"""Tests for envchain.env_merge."""

import pytest

from envchain.env_merge import EnvMerger, MergeConflict, MergeStrategy


@pytest.fixture
def merger():
    return EnvMerger()


P1 = {"DB_HOST": "localhost", "DB_PORT": "5432", "SHARED": "from-p1"}
P2 = {"APP_ENV": "production", "SHARED": "from-p2", "EXTRA": "yes"}
P3 = {"SHARED": "from-p3", "ONLY_P3": "value"}


# ---------------------------------------------------------------------------
# MergeResult helpers
# ---------------------------------------------------------------------------

class TestMergeResult:
    def test_has_conflicts_false_when_no_overlap(self, merger):
        result = merger.merge({"a": {"X": "1"}, "b": {"Y": "2"}})
        assert not result.has_conflicts

    def test_has_conflicts_true_when_overlap(self, merger):
        result = merger.merge({"a": P1, "b": P2})
        assert result.has_conflicts

    def test_repr_contains_counts(self, merger):
        result = merger.merge({"a": {"X": "1"}})
        r = repr(result)
        assert "vars=" in r
        assert "conflicts=" in r

    def test_conflict_summary_no_conflicts(self, merger):
        result = merger.merge({"a": {"X": "1"}})
        assert result.conflict_summary() == "No conflicts."

    def test_conflict_summary_lists_keys(self, merger):
        result = merger.merge({"p1": P1, "p2": P2})
        summary = result.conflict_summary()
        assert "SHARED" in summary
        assert "p1" in summary
        assert "p2" in summary


# ---------------------------------------------------------------------------
# LAST_WINS (default)
# ---------------------------------------------------------------------------

class TestLastWins:
    def test_last_profile_value_wins(self, merger):
        result = merger.merge({"p1": P1, "p2": P2})
        assert result.merged["SHARED"] == "from-p2"

    def test_non_conflicting_keys_all_present(self, merger):
        result = merger.merge({"p1": P1, "p2": P2})
        assert result.merged["DB_HOST"] == "localhost"
        assert result.merged["APP_ENV"] == "production"

    def test_three_profiles_last_wins(self, merger):
        result = merger.merge({"p1": P1, "p2": P2, "p3": P3})
        assert result.merged["SHARED"] == "from-p3"


# ---------------------------------------------------------------------------
# FIRST_WINS
# ---------------------------------------------------------------------------

class TestFirstWins:
    def test_first_profile_value_kept(self, merger):
        result = merger.merge(
            {"p1": P1, "p2": P2}, strategy=MergeStrategy.FIRST_WINS
        )
        assert result.merged["SHARED"] == "from-p1"

    def test_unique_keys_still_included(self, merger):
        result = merger.merge(
            {"p1": P1, "p2": P2}, strategy=MergeStrategy.FIRST_WINS
        )
        assert "EXTRA" in result.merged


# ---------------------------------------------------------------------------
# STRICT
# ---------------------------------------------------------------------------

class TestStrict:
    def test_no_overlap_succeeds(self, merger):
        result = merger.merge(
            {"a": {"X": "1"}, "b": {"Y": "2"}},
            strategy=MergeStrategy.STRICT,
        )
        assert result.merged == {"X": "1", "Y": "2"}

    def test_overlap_raises_merge_conflict(self, merger):
        with pytest.raises(MergeConflict) as exc_info:
            merger.merge({"p1": P1, "p2": P2}, strategy=MergeStrategy.STRICT)
        assert exc_info.value.key == "SHARED"
        assert "p1" in exc_info.value.profiles
        assert "p2" in exc_info.value.profiles

    def test_merge_conflict_message(self, merger):
        with pytest.raises(MergeConflict) as exc_info:
            merger.merge({"p1": P1, "p2": P2}, strategy=MergeStrategy.STRICT)
        assert "SHARED" in str(exc_info.value)


# ---------------------------------------------------------------------------
# exclude_keys
# ---------------------------------------------------------------------------

class TestExcludeKeys:
    def test_excluded_key_not_in_result(self, merger):
        result = merger.merge({"p1": P1, "p2": P2}, exclude_keys=["SHARED"])
        assert "SHARED" not in result.merged

    def test_excluded_key_not_counted_as_conflict(self, merger):
        result = merger.merge({"p1": P1, "p2": P2}, exclude_keys=["SHARED"])
        assert not result.has_conflicts

    def test_other_keys_unaffected(self, merger):
        result = merger.merge({"p1": P1, "p2": P2}, exclude_keys=["SHARED"])
        assert "DB_HOST" in result.merged
        assert "APP_ENV" in result.merged
