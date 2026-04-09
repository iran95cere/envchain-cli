"""Tests for envchain.diff module."""

import pytest
from envchain.diff import DiffResult, ProfileDiffer


@pytest.fixture
def differ():
    return ProfileDiffer()


class TestDiffResult:
    def test_has_changes_false_when_empty(self):
        result = DiffResult()
        assert not result.has_changes

    def test_has_changes_true_when_added(self):
        result = DiffResult(added={"FOO": "bar"})
        assert result.has_changes

    def test_has_changes_true_when_removed(self):
        result = DiffResult(removed={"FOO": "bar"})
        assert result.has_changes

    def test_has_changes_true_when_modified(self):
        result = DiffResult(modified={"FOO": ("old", "new")})
        assert result.has_changes

    def test_summary_no_changes(self):
        result = DiffResult()
        assert result.summary() == "No changes"

    def test_summary_with_changes(self):
        result = DiffResult(
            added={"A": "1"},
            removed={"B": "2", "C": "3"},
            modified={"D": ("x", "y")},
        )
        summary = result.summary()
        assert "+1 added" in summary
        assert "-2 removed" in summary
        assert "~1 modified" in summary

    def test_to_lines_prefixes(self):
        result = DiffResult(
            added={"NEW": "val"},
            removed={"OLD": "val"},
            modified={"MOD": ("a", "b")},
            unchanged={"SAME": "v"},
        )
        lines = result.to_lines()
        assert any(l.startswith("+ NEW") for l in lines)
        assert any(l.startswith("- OLD") for l in lines)
        assert any(l.startswith("~ MOD") for l in lines)
        assert any(l.startswith("  SAME") for l in lines)

    def test_to_lines_show_values(self):
        result = DiffResult(added={"KEY": "secret"})
        lines = result.to_lines(show_values=True)
        assert any("secret" in l for l in lines)

    def test_to_lines_hide_values_by_default(self):
        result = DiffResult(added={"KEY": "secret"})
        lines = result.to_lines()
        assert not any("secret" in l for l in lines)


class TestProfileDiffer:
    def test_identical_profiles_no_changes(self, differ):
        vars_ = {"A": "1", "B": "2"}
        result = differ.diff(vars_, vars_)
        assert not result.has_changes
        assert result.unchanged == vars_

    def test_added_keys(self, differ):
        result = differ.diff({}, {"NEW": "val"})
        assert "NEW" in result.added
        assert result.added["NEW"] == "val"

    def test_removed_keys(self, differ):
        result = differ.diff({"OLD": "val"}, {})
        assert "OLD" in result.removed

    def test_modified_keys(self, differ):
        result = differ.diff({"K": "old"}, {"K": "new"})
        assert "K" in result.modified
        assert result.modified["K"] == ("old", "new")

    def test_mixed_changes(self, differ):
        base = {"A": "1", "B": "2", "C": "3"}
        target = {"A": "1", "B": "changed", "D": "4"}
        result = differ.diff(base, target)
        assert "A" in result.unchanged
        assert "B" in result.modified
        assert "C" in result.removed
        assert "D" in result.added
