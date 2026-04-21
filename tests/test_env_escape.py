"""Tests for envchain.env_escape."""
from __future__ import annotations

import pytest

from envchain.env_escape import EnvEscaper, EscapeReport, EscapeResult


@pytest.fixture
def escaper() -> EnvEscaper:
    return EnvEscaper()


@pytest.fixture
def sample_vars() -> dict:
    return {
        "PLAIN": "hello",
        "QUOTED": 'say "hi"',
        "DOLLAR": "cost $5",
        "BACKTICK": "run `cmd`",
        "BACKSLASH": "path\\to\\file",
    }


class TestEscapeResult:
    def test_changed_true_when_values_differ(self):
        r = EscapeResult(name="X", original="hello", escaped="hello_esc")
        assert r.changed is True

    def test_changed_false_when_values_same(self):
        r = EscapeResult(name="X", original="hello", escaped="hello")
        assert r.changed is False

    def test_repr_contains_name(self):
        r = EscapeResult(name="MY_VAR", original="a", escaped="b")
        assert "MY_VAR" in repr(r)

    def test_repr_status_changed(self):
        r = EscapeResult(name="X", original="a", escaped="b")
        assert "changed" in repr(r)

    def test_repr_status_unchanged(self):
        r = EscapeResult(name="X", original="a", escaped="a")
        assert "unchanged" in repr(r)


class TestEscapeReport:
    def test_changed_count_zero_when_clean(self, escaper):
        report = escaper.escape({"A": "simple", "B": "value"})
        assert report.changed_count == 0

    def test_has_changes_false_when_clean(self, escaper):
        report = escaper.escape({"A": "plain"})
        assert report.has_changes is False

    def test_has_changes_true_when_special(self, escaper):
        report = escaper.escape({"A": 'say "hello"'})
        assert report.has_changes is True

    def test_changed_count_matches_modified(self, escaper, sample_vars):
        report = escaper.escape(sample_vars)
        # PLAIN has no special chars; the rest do
        assert report.changed_count == 4

    def test_to_dict_returns_escaped_values(self, escaper):
        report = escaper.escape({"K": 'val"ue'})
        d = report.to_dict()
        assert '"' not in d["K"] or d["K"].count('\\"') >= 1

    def test_repr_contains_counts(self, escaper, sample_vars):
        report = escaper.escape(sample_vars)
        r = repr(report)
        assert "total=" in r
        assert "changed=" in r


class TestEnvEscaper:
    def test_escape_double_quote(self, escaper):
        result = escaper._escape_value('He said "hi"')
        assert '\\"' in result

    def test_escape_dollar(self, escaper):
        result = escaper._escape_value("cost $10")
        assert "\\$" in result

    def test_escape_backtick(self, escaper):
        result = escaper._escape_value("run `ls`")
        assert "\\`" in result

    def test_escape_backslash(self, escaper):
        result = escaper._escape_value("C:\\Users")
        assert "\\\\" in result

    def test_plain_value_unchanged(self, escaper):
        assert escaper._escape_value("hello_world") == "hello_world"

    def test_unescape_roundtrip(self, escaper):
        original = {"A": 'say "hi"', "B": "cost $5"}
        escaped_report = escaper.escape(original)
        unescaped = escaper.unescape(escaped_report.to_dict())
        assert unescaped == original

    def test_unescape_plain_unchanged(self, escaper):
        result = escaper.unescape({"X": "plain"})
        assert result["X"] == "plain"
