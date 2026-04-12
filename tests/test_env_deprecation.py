"""Tests for envchain.env_deprecation."""
import pytest
from envchain.env_deprecation import DeprecationChecker, DeprecationEntry, DeprecationReport


@pytest.fixture
def checker():
    return DeprecationChecker()


class TestDeprecationEntry:
    def test_to_dict_contains_required_keys(self):
        entry = DeprecationEntry(var_name="OLD_KEY", replacement="NEW_KEY", reason="renamed")
        d = entry.to_dict()
        assert "var_name" in d
        assert "replacement" in d
        assert "reason" in d
        assert "deprecated_at" in d

    def test_from_dict_roundtrip(self):
        entry = DeprecationEntry(var_name="OLD_KEY", replacement="NEW_KEY", reason="renamed")
        restored = DeprecationEntry.from_dict(entry.to_dict())
        assert restored.var_name == entry.var_name
        assert restored.replacement == entry.replacement
        assert restored.reason == entry.reason

    def test_repr_contains_var_name(self):
        entry = DeprecationEntry(var_name="OLD_KEY", replacement=None, reason="unused")
        assert "OLD_KEY" in repr(entry)

    def test_repr_contains_replacement_when_set(self):
        entry = DeprecationEntry(var_name="OLD_KEY", replacement="NEW_KEY", reason="renamed")
        assert "NEW_KEY" in repr(entry)


class TestDeprecationReport:
    def test_has_deprecated_false_when_empty(self):
        report = DeprecationReport()
        assert not report.has_deprecated

    def test_has_deprecated_true_when_entries(self):
        entry = DeprecationEntry(var_name="X", replacement=None, reason="old")
        report = DeprecationReport(entries=[entry], checked_vars=["X"])
        assert report.has_deprecated

    def test_deprecated_count(self):
        entries = [
            DeprecationEntry(var_name="A", replacement=None, reason="r"),
            DeprecationEntry(var_name="B", replacement=None, reason="r"),
        ]
        report = DeprecationReport(entries=entries)
        assert report.deprecated_count == 2

    def test_repr_contains_counts(self):
        report = DeprecationReport()
        assert "deprecated=0" in repr(report)


class TestDeprecationChecker:
    def test_register_and_check_flags_deprecated(self, checker):
        checker.register("OLD_TOKEN", reason="renamed", replacement="API_TOKEN")
        report = checker.check({"OLD_TOKEN": "abc", "OTHER": "xyz"})
        assert report.has_deprecated
        assert report.entries[0].var_name == "OLD_TOKEN"

    def test_check_case_insensitive(self, checker):
        checker.register("OLD_KEY", reason="renamed")
        report = checker.check({"old_key": "val"})
        assert report.has_deprecated

    def test_check_no_match_returns_empty_report(self, checker):
        checker.register("OLD_KEY", reason="renamed")
        report = checker.check({"NEW_KEY": "val"})
        assert not report.has_deprecated

    def test_register_empty_name_raises(self, checker):
        with pytest.raises(ValueError):
            checker.register("", reason="bad")

    def test_unregister_removes_entry(self, checker):
        checker.register("OLD_KEY", reason="renamed")
        result = checker.unregister("OLD_KEY")
        assert result is True
        assert checker.check({"OLD_KEY": "v"}).deprecated_count == 0

    def test_unregister_missing_returns_false(self, checker):
        assert checker.unregister("NONEXISTENT") is False

    def test_all_deprecated_lists_entries(self, checker):
        checker.register("A", reason="r")
        checker.register("B", reason="r")
        assert len(checker.all_deprecated()) == 2
