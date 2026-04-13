"""Tests for envchain.env_trim."""
from __future__ import annotations

import pytest
from envchain.env_trim import EnvTrimmer, TrimResult, TrimReport


@pytest.fixture
def trimmer():
    return EnvTrimmer()


class TestTrimResult:
    def test_changed_true_when_values_differ(self):
        r = TrimResult(name="FOO", original_value="  bar  ", trimmed_value="bar")
        assert r.changed is True

    def test_changed_false_when_values_same(self):
        r = TrimResult(name="FOO", original_value="bar", trimmed_value="bar")
        assert r.changed is False

    def test_repr_contains_name(self):
        r = TrimResult(name="FOO", original_value="  x", trimmed_value="x")
        assert "FOO" in repr(r)

    def test_repr_contains_changed_status(self):
        r = TrimResult(name="FOO", original_value="  x", trimmed_value="x")
        assert "changed" in repr(r)


class TestTrimReport:
    def test_changed_count_zero_when_clean(self):
        report = TrimReport(results=[
            TrimResult("A", "val", "val"),
            TrimResult("B", "val2", "val2"),
        ])
        assert report.changed_count == 0

    def test_changed_count_correct(self):
        report = TrimReport(results=[
            TrimResult("A", "  val", "val"),
            TrimResult("B", "val2", "val2"),
        ])
        assert report.changed_count == 1

    def test_has_changes_false_when_clean(self):
        report = TrimReport()
        assert report.has_changes is False

    def test_has_changes_true_when_dirty(self):
        report = TrimReport(results=[TrimResult("X", " a ", "a")])
        assert report.has_changes is True

    def test_changed_vars_filters_correctly(self):
        report = TrimReport(results=[
            TrimResult("A", "  v", "v"),
            TrimResult("B", "ok", "ok"),
        ])
        assert len(report.changed_vars()) == 1
        assert report.changed_vars()[0].name == "A"

    def test_to_dict_contains_required_keys(self):
        report = TrimReport(results=[TrimResult("A", " v", "v")])
        d = report.to_dict()
        assert "changed_count" in d
        assert "results" in d


class TestEnvTrimmer:
    def test_trim_strips_leading_trailing(self, trimmer):
        trimmed, report = trimmer.trim({"FOO": "  hello  "})
        assert trimmed["FOO"] == "hello"
        assert report.changed_count == 1

    def test_trim_no_change_when_clean(self, trimmer):
        trimmed, report = trimmer.trim({"FOO": "hello"})
        assert trimmed["FOO"] == "hello"
        assert report.changed_count == 0

    def test_trim_multiple_vars(self, trimmer):
        variables = {"A": " val ", "B": "clean", "C": "\ttab\t"}
        trimmed, report = trimmer.trim(variables)
        assert trimmed["A"] == "val"
        assert trimmed["B"] == "clean"
        assert trimmed["C"] == "tab"
        assert report.changed_count == 2

    def test_trim_names_strips_key_whitespace(self, trimmer):
        result, renamed = trimmer.trim_names({" FOO ": "bar"})
        assert "FOO" in result
        assert " FOO " in renamed

    def test_trim_names_unchanged_keys_not_in_renamed(self, trimmer):
        result, renamed = trimmer.trim_names({"FOO": "bar"})
        assert "FOO" in result
        assert renamed == []
