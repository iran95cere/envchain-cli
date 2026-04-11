"""Tests for envchain.env_compare."""
import pytest
from envchain.env_compare import CompareEntry, CompareResult, ProfileComparer


@pytest.fixture
def comparer() -> ProfileComparer:
    return ProfileComparer()


class TestCompareEntry:
    def test_is_same_when_values_equal(self):
        e = CompareEntry("KEY", "val", "val")
        assert e.is_same is True

    def test_is_same_false_when_different(self):
        e = CompareEntry("KEY", "a", "b")
        assert e.is_same is False

    def test_only_in_left(self):
        e = CompareEntry("KEY", "val", None)
        assert e.only_in_left is True
        assert e.only_in_right is False

    def test_only_in_right(self):
        e = CompareEntry("KEY", None, "val")
        assert e.only_in_right is True
        assert e.only_in_left is False

    def test_is_modified(self):
        e = CompareEntry("KEY", "old", "new")
        assert e.is_modified is True

    def test_is_modified_false_when_same(self):
        e = CompareEntry("KEY", "same", "same")
        assert e.is_modified is False

    def test_repr_contains_name(self):
        e = CompareEntry("MY_VAR", "x", "y")
        assert "MY_VAR" in repr(e)


class TestCompareResult:
    def test_has_differences_false_when_identical(self):
        result = CompareResult("a", "b", [CompareEntry("K", "v", "v")])
        assert result.has_differences is False

    def test_has_differences_true_when_added(self):
        result = CompareResult("a", "b", [CompareEntry("K", None, "v")])
        assert result.has_differences is True

    def test_summary_format(self):
        result = CompareResult(
            "a",
            "b",
            [
                CompareEntry("A", "x", "x"),
                CompareEntry("B", None, "y"),
                CompareEntry("C", "z", None),
                CompareEntry("D", "old", "new"),
            ],
        )
        s = result.summary()
        assert "same=1" in s
        assert "added=1" in s
        assert "removed=1" in s
        assert "modified=1" in s


class TestProfileComparer:
    def test_compare_identical_profiles(self, comparer):
        vars_ = {"A": "1", "B": "2"}
        result = comparer.compare(vars_, vars_, "p1", "p2")
        assert not result.has_differences
        assert len(result.same) == 2

    def test_compare_detects_added(self, comparer):
        result = comparer.compare({}, {"NEW": "val"}, "p1", "p2")
        assert len(result.added) == 1
        assert result.added[0].name == "NEW"

    def test_compare_detects_removed(self, comparer):
        result = comparer.compare({"OLD": "val"}, {}, "p1", "p2")
        assert len(result.removed) == 1

    def test_compare_detects_modified(self, comparer):
        result = comparer.compare({"K": "old"}, {"K": "new"}, "p1", "p2")
        assert len(result.modified) == 1
        assert result.modified[0].left_value == "old"
        assert result.modified[0].right_value == "new"

    def test_entries_sorted_by_name(self, comparer):
        result = comparer.compare({"Z": "1", "A": "2"}, {"Z": "1", "A": "2"}, "p1", "p2")
        names = [e.name for e in result.entries]
        assert names == sorted(names)

    def test_profile_names_stored(self, comparer):
        result = comparer.compare({}, {}, "alpha", "beta")
        assert result.left_profile == "alpha"
        assert result.right_profile == "beta"
