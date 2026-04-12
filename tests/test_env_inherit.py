"""Tests for envchain.env_inherit."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from envchain.env_inherit import InheritanceError, InheritanceResult, ProfileInheriter


def _make_storage(profiles: dict) -> MagicMock:
    storage = MagicMock()

    def _load(name, password):
        profile = MagicMock()
        profile.variables = profiles.get(name, {})
        return profile

    storage.load_profile.side_effect = _load
    return storage


@pytest.fixture()
def simple_storage():
    return _make_storage(
        {
            "base": {"HOST": "localhost", "PORT": "5432"},
            "dev": {"PORT": "5433", "DEBUG": "true"},
        }
    )


@pytest.fixture()
def inheriter(simple_storage):
    return ProfileInheriter(simple_storage)


# --- InheritanceResult unit tests ---

class TestInheritanceResult:
    def test_var_count(self):
        r = InheritanceResult("p", resolved_vars={"A": "1", "B": "2"})
        assert r.var_count == 2

    def test_override_count(self):
        r = InheritanceResult("p", overridden_keys=["X", "Y"])
        assert r.override_count == 2

    def test_repr_contains_profile_name(self):
        r = InheritanceResult("myprofile")
        assert "myprofile" in repr(r)

    def test_repr_contains_chain(self):
        r = InheritanceResult("child", chain=["base", "child"])
        assert "base" in repr(r)
        assert "child" in repr(r)


# --- ProfileInheriter tests ---

class TestProfileInheriter:
    def test_resolve_no_parent_returns_child_vars(self, inheriter):
        result = inheriter.resolve("dev", None, "secret")
        assert result.resolved_vars == {"PORT": "5433", "DEBUG": "true"}
        assert result.chain == ["dev"]

    def test_resolve_with_parent_merges_vars(self, inheriter):
        result = inheriter.resolve("dev", "base", "secret")
        assert result.resolved_vars["HOST"] == "localhost"  # from parent
        assert result.resolved_vars["DEBUG"] == "true"      # from child

    def test_child_overrides_parent_value(self, inheriter):
        result = inheriter.resolve("dev", "base", "secret")
        assert result.resolved_vars["PORT"] == "5433"  # child wins

    def test_overridden_keys_tracked(self, inheriter):
        result = inheriter.resolve("dev", "base", "secret")
        assert "PORT" in result.overridden_keys

    def test_chain_ordered_parent_then_child(self, inheriter):
        result = inheriter.resolve("dev", "base", "secret")
        assert result.chain == ["base", "dev"]

    def test_cycle_detection_raises(self):
        storage = _make_storage({"a": {}, "b": {}})
        inheriter = ProfileInheriter(storage)
        with pytest.raises(InheritanceError, match="Circular"):
            inheriter.resolve("a", "a", "pw", _visited=["a"])

    def test_empty_parent_profile_still_resolves(self):
        storage = _make_storage({"empty": {}, "child": {"X": "1"}})
        inheriter = ProfileInheriter(storage)
        result = inheriter.resolve("child", "empty", "pw")
        assert result.resolved_vars == {"X": "1"}
        assert result.overridden_keys == []
