"""Tests for envchain.env_format and envchain.cli_format."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from envchain.env_format import EnvFormatter, FormatReport, FormatResult
from envchain.cli_format import FormatCommand


@pytest.fixture()
def formatter() -> EnvFormatter:
    return EnvFormatter()


# ---------------------------------------------------------------------------
# FormatResult
# ---------------------------------------------------------------------------

class TestFormatResult:
    def test_changed_true_when_values_differ(self):
        r = FormatResult(original="  hi  ", formatted="hi", fmt_type="trim", changed=True)
        assert r.changed is True

    def test_changed_false_when_values_same(self):
        r = FormatResult(original="hi", formatted="hi", fmt_type="trim", changed=False)
        assert r.changed is False


# ---------------------------------------------------------------------------
# FormatReport
# ---------------------------------------------------------------------------

class TestFormatReport:
    def test_changed_count_zero_when_no_changes(self):
        report = FormatReport()
        assert report.changed_count == 0
        assert report.has_changes is False

    def test_changed_count_reflects_changed_results(self):
        report = FormatReport(results=[
            FormatResult("a", "a", "trim", False),
            FormatResult("b", "B", "upper", True),
        ])
        assert report.changed_count == 1
        assert report.has_changes is True

    def test_to_dict_contains_required_keys(self):
        report = FormatReport()
        d = report.to_dict()
        assert "changed_count" in d
        assert "results" in d


# ---------------------------------------------------------------------------
# EnvFormatter
# ---------------------------------------------------------------------------

class TestEnvFormatter:
    def test_trim_removes_whitespace(self, formatter):
        result = formatter.format_value("  hello  ", "trim")
        assert result.formatted == "hello"
        assert result.changed is True

    def test_trim_no_change_when_clean(self, formatter):
        result = formatter.format_value("hello", "trim")
        assert result.changed is False

    def test_upper_converts_to_uppercase(self, formatter):
        result = formatter.format_value("hello", "upper")
        assert result.formatted == "HELLO"
        assert result.changed is True

    def test_lower_converts_to_lowercase(self, formatter):
        result = formatter.format_value("HELLO", "lower")
        assert result.formatted == "hello"
        assert result.changed is True

    def test_strip_quotes_removes_double_quotes(self, formatter):
        result = formatter.format_value('"value"', "strip_quotes")
        assert result.formatted == "value"
        assert result.changed is True

    def test_strip_quotes_removes_single_quotes(self, formatter):
        result = formatter.format_value("'value'", "strip_quotes")
        assert result.formatted == "value"
        assert result.changed is True

    def test_strip_quotes_no_change_when_unquoted(self, formatter):
        result = formatter.format_value("value", "strip_quotes")
        assert result.changed is False

    def test_unknown_format_raises_value_error(self, formatter):
        with pytest.raises(ValueError, match="Unknown format type"):
            formatter.format_value("x", "unknown")

    def test_format_vars_applies_to_all_keys(self, formatter):
        report = formatter.format_vars({"A": "  a  ", "B": "  b  "}, "trim")
        assert report.changed_count == 2

    def test_format_vars_applies_to_selected_keys_only(self, formatter):
        report = formatter.format_vars({"A": "  a  ", "B": "  b  "}, "trim", keys=["A"])
        assert report.changed_count == 1

    def test_format_vars_skips_missing_keys_silently(self, formatter):
        report = formatter.format_vars({"A": "hello"}, "upper", keys=["A", "MISSING"])
        assert len(report.results) == 1


# ---------------------------------------------------------------------------
# FormatCommand (CLI)
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_storage():
    storage = MagicMock()
    profile = MagicMock()
    profile.variables = {"KEY": "  value  ", "OTHER": "clean"}
    storage.load_profile.return_value = profile
    return storage


@pytest.fixture()
def cmd(mock_storage):
    return FormatCommand(mock_storage)


class TestFormatCommand:
    def test_run_saves_profile_on_changes(self, cmd, mock_storage, capsys):
        cmd.run("dev", "trim", "pass")
        mock_storage.save_profile.assert_called_once()
        out = capsys.readouterr().out
        assert "Updated" in out

    def test_run_dry_run_does_not_save(self, cmd, mock_storage, capsys):
        cmd.run("dev", "trim", "pass", dry_run=True)
        mock_storage.save_profile.assert_not_called()
        out = capsys.readouterr().out
        assert "dry-run" in out

    def test_run_no_changes_prints_message(self, cmd, mock_storage, capsys):
        mock_storage.load_profile.return_value.variables = {"KEY": "clean"}
        cmd.run("dev", "trim", "pass")
        out = capsys.readouterr().out
        assert "No changes" in out

    def test_run_unknown_format_exits(self, cmd, capsys):
        with pytest.raises(SystemExit):
            cmd.run("dev", "bogus", "pass")

    def test_run_missing_profile_exits(self, cmd, mock_storage, capsys):
        mock_storage.load_profile.return_value = None
        with pytest.raises(SystemExit):
            cmd.run("dev", "trim", "pass")

    def test_list_formats_prints_all(self, cmd, capsys):
        cmd.list_formats()
        out = capsys.readouterr().out
        for fmt in EnvFormatter.SUPPORTED_FORMATS:
            assert fmt in out
