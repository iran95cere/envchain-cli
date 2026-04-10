"""Tests for envchain.lint module."""
import pytest

from envchain.lint import LintIssue, LintReport, ProfileLinter


@pytest.fixture()
def linter() -> ProfileLinter:
    return ProfileLinter()


# ---------------------------------------------------------------------------
# LintReport helpers
# ---------------------------------------------------------------------------


class TestLintReport:
    def test_has_errors_false_when_empty(self):
        assert not LintReport().has_errors

    def test_has_warnings_false_when_empty(self):
        assert not LintReport().has_warnings

    def test_has_errors_true(self):
        r = LintReport(issues=[LintIssue("error", "KEY", "bad")])
        assert r.has_errors

    def test_has_warnings_true(self):
        r = LintReport(issues=[LintIssue("warning", "KEY", "meh")])
        assert r.has_warnings

    def test_summary_counts(self):
        r = LintReport(
            issues=[
                LintIssue("error", "A", "e"),
                LintIssue("warning", "B", "w"),
                LintIssue("warning", "C", "w2"),
            ]
        )
        assert r.summary() == "1 error(s), 2 warning(s)"

    def test_summary_no_issues(self):
        assert LintReport().summary() == "0 error(s), 0 warning(s)"


# ---------------------------------------------------------------------------
# ProfileLinter rules
# ---------------------------------------------------------------------------


class TestProfileLinter:
    def test_clean_vars_produce_no_issues(self, linter):
        report = linter.lint({"DATABASE_URL": "postgres://localhost/db"})
        assert report.issues == []

    def test_empty_value_triggers_warning(self, linter):
        report = linter.lint({"API_KEY": ""})
        assert any("empty" in i.message.lower() for i in report.issues)

    def test_whitespace_only_value_triggers_warning(self, linter):
        report = linter.lint({"SECRET": "   "})
        messages = [i.message for i in report.issues]
        assert any("empty" in m.lower() for m in messages)

    def test_placeholder_triggers_warning(self, linter):
        report = linter.lint({"TOKEN": "<your-token-here>"})
        assert any("placeholder" in i.message.lower() for i in report.issues)

    def test_todo_placeholder_detected(self, linter):
        report = linter.lint({"SECRET": "TODO"})
        assert any("placeholder" in i.message.lower() for i in report.issues)

    def test_lowercase_key_triggers_warning(self, linter):
        report = linter.lint({"my_var": "value"})
        assert any("UPPER_CASE" in i.message for i in report.issues)

    def test_mixed_case_key_triggers_warning(self, linter):
        report = linter.lint({"MyVar": "value"})
        assert any("UPPER_CASE" in i.message for i in report.issues)

    def test_leading_whitespace_in_value(self, linter):
        report = linter.lint({"HOST": "  localhost"})
        assert any("whitespace" in i.message.lower() for i in report.issues)

    def test_trailing_whitespace_in_value(self, linter):
        report = linter.lint({"HOST": "localhost  "})
        assert any("whitespace" in i.message.lower() for i in report.issues)

    def test_multiple_vars_accumulate_issues(self, linter):
        """Issues from multiple variables are all collected in one report."""
        report = linter.lint({
            "good_key": "value",
            "BAD_VALUE": "",
        })
        keys_with_issues = {i.key for i in report.issues}
        assert "good_key" in keys_with_issues
        assert "BAD_VALUE" in keys_with_issues
