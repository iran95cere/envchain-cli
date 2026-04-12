"""Tests for envchain.env_cascade."""
import pytest

from envchain.env_cascade import CascadeSource, CascadeResult, EnvCascade


@pytest.fixture()
def cascade() -> EnvCascade:
    return EnvCascade()


# ---------------------------------------------------------------------------
# CascadeSource
# ---------------------------------------------------------------------------

class TestCascadeSource:
    def test_repr_contains_profile(self):
        src = CascadeSource(profile="dev", value="val", priority=0)
        assert "dev" in repr(src)

    def test_repr_contains_priority(self):
        src = CascadeSource(profile="dev", value="val", priority=2)
        assert "2" in repr(src)


# ---------------------------------------------------------------------------
# CascadeResult
# ---------------------------------------------------------------------------

class TestCascadeResult:
    def test_var_count_empty(self):
        r = CascadeResult()
        assert r.var_count == 0

    def test_to_flat_dict(self):
        r = CascadeResult(
            resolved={"KEY": CascadeSource("dev", "hello", 0)},
            profiles_used=["dev"],
        )
        assert r.to_flat_dict() == {"KEY": "hello"}

    def test_source_for_missing_returns_none(self):
        r = CascadeResult()
        assert r.source_for("MISSING") is None

    def test_repr_contains_var_count(self):
        r = CascadeResult(
            resolved={"A": CascadeSource("p", "v", 0)},
            profiles_used=["p"],
        )
        assert "1" in repr(r)


# ---------------------------------------------------------------------------
# EnvCascade.resolve
# ---------------------------------------------------------------------------

class TestEnvCascade:
    def test_single_profile_all_vars_included(self, cascade):
        result = cascade.resolve([("dev", {"A": "1", "B": "2"})])
        assert result.to_flat_dict() == {"A": "1", "B": "2"}

    def test_higher_priority_profile_wins(self, cascade):
        result = cascade.resolve([
            ("dev", {"KEY": "dev_val"}),
            ("base", {"KEY": "base_val"}),
        ])
        assert result.to_flat_dict()["KEY"] == "dev_val"

    def test_lower_priority_fills_missing_vars(self, cascade):
        result = cascade.resolve([
            ("dev", {"A": "from_dev"}),
            ("base", {"A": "from_base", "B": "from_base"}),
        ])
        flat = result.to_flat_dict()
        assert flat["A"] == "from_dev"
        assert flat["B"] == "from_base"

    def test_source_profile_recorded(self, cascade):
        result = cascade.resolve([
            ("dev", {"A": "1"}),
            ("base", {"B": "2"}),
        ])
        assert result.source_for("A").profile == "dev"
        assert result.source_for("B").profile == "base"

    def test_profiles_used_order_preserved(self, cascade):
        result = cascade.resolve([
            ("high", {}),
            ("mid", {}),
            ("low", {}),
        ])
        assert result.profiles_used == ["high", "mid", "low"]

    def test_empty_profiles_returns_empty_result(self, cascade):
        result = cascade.resolve([])
        assert result.var_count == 0
        assert result.profiles_used == []

    def test_priority_index_correct(self, cascade):
        result = cascade.resolve([
            ("first", {"X": "1"}),
            ("second", {"Y": "2"}),
        ])
        assert result.source_for("X").priority == 0
        assert result.source_for("Y").priority == 1
