"""Tests for envchain.env_priority."""
import pytest

from envchain.env_priority import EnvPriority, PriorityEntry, PriorityResult


@pytest.fixture
def resolver():
    return EnvPriority()


# ---------------------------------------------------------------------------
# PriorityEntry
# ---------------------------------------------------------------------------

class TestPriorityEntry:
    def test_to_dict_contains_required_keys(self):
        e = PriorityEntry(var_name="DB_URL", value="postgres://", profile="prod", priority=10)
        d = e.to_dict()
        assert {"var_name", "value", "profile", "priority"} <= d.keys()

    def test_from_dict_roundtrip(self):
        original = PriorityEntry(var_name="KEY", value="abc", profile="dev", priority=5)
        restored = PriorityEntry.from_dict(original.to_dict())
        assert restored.var_name == original.var_name
        assert restored.value == original.value
        assert restored.profile == original.profile
        assert restored.priority == original.priority

    def test_repr_contains_var_and_profile(self):
        e = PriorityEntry(var_name="X", value="1", profile="base", priority=0)
        r = repr(e)
        assert "X" in r
        assert "base" in r


# ---------------------------------------------------------------------------
# PriorityResult
# ---------------------------------------------------------------------------

class TestPriorityResult:
    def test_var_count_empty(self):
        assert PriorityResult().var_count == 0

    def test_has_conflicts_false_when_empty(self):
        assert not PriorityResult().has_conflicts()

    def test_to_flat_dict_returns_values(self):
        pr = PriorityResult()
        pr.resolved["A"] = PriorityEntry("A", "1", "p", 1)
        assert pr.to_flat_dict() == {"A": "1"}

    def test_repr_contains_counts(self):
        r = repr(PriorityResult())
        assert "vars=" in r
        assert "conflicts=" in r


# ---------------------------------------------------------------------------
# EnvPriority.resolve
# ---------------------------------------------------------------------------

class TestEnvPriority:
    def test_single_profile_resolved(self, resolver):
        result = resolver.resolve([("dev", {"A": "1", "B": "2"}, 1)])
        assert result.var_count == 2
        assert result.to_flat_dict() == {"A": "1", "B": "2"}

    def test_higher_priority_wins(self, resolver):
        result = resolver.resolve([
            ("base", {"A": "low"}, 1),
            ("prod", {"A": "high"}, 10),
        ])
        assert result.resolved["A"].value == "high"
        assert result.resolved["A"].profile == "prod"

    def test_lower_priority_does_not_override(self, resolver):
        result = resolver.resolve([
            ("prod", {"X": "prod_val"}, 10),
            ("base", {"X": "base_val"}, 1),
        ])
        assert result.to_flat_dict()["X"] == "prod_val"

    def test_no_conflict_when_unique_keys(self, resolver):
        result = resolver.resolve([
            ("a", {"FOO": "1"}, 5),
            ("b", {"BAR": "2"}, 5),
        ], track_conflicts=True)
        assert not result.has_conflicts()

    def test_conflict_tracked_when_same_key_different_profiles(self, resolver):
        result = resolver.resolve([
            ("a", {"KEY": "v1"}, 5),
            ("b", {"KEY": "v2"}, 3),
        ], track_conflicts=True)
        assert result.has_conflicts()
        assert "KEY" in result.conflicts
        assert result.conflict_count == 1

    def test_empty_profiles_returns_empty_result(self, resolver):
        result = resolver.resolve([])
        assert result.var_count == 0
        assert not result.has_conflicts()

    def test_equal_priority_first_listed_wins(self, resolver):
        result = resolver.resolve([
            ("first", {"Z": "first_val"}, 5),
            ("second", {"Z": "second_val"}, 5),
        ])
        # max() is stable for equal keys; first entry encountered wins
        assert result.resolved["Z"].value == "first_val"
