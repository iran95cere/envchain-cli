"""Tests for envchain.env_placeholder."""
import pytest
from envchain.env_placeholder import (
    PlaceholderChecker,
    PlaceholderIssue,
    PlaceholderReport,
)


@pytest.fixture
def checker() -> PlaceholderChecker:
    return PlaceholderChecker()


class TestPlaceholderIssue:
    def test_repr_contains_var_and_placeholder(self):
        issue = PlaceholderIssue(var_name="URL", placeholder="${HOST}")
        r = repr(issue)
        assert "URL" in r
        assert "${HOST}" in r


class TestPlaceholderReport:
    def test_has_issues_false_when_empty(self):
        report = PlaceholderReport(profile_name="dev")
        assert not report.has_issues

    def test_has_issues_true_when_populated(self):
        report = PlaceholderReport(
            profile_name="dev",
            issues=[PlaceholderIssue("URL", "${HOST}")],
        )
        assert report.has_issues

    def test_issue_count(self):
        report = PlaceholderReport(
            profile_name="dev",
            issues=[
                PlaceholderIssue("A", "${X}"),
                PlaceholderIssue("B", "$Y"),
            ],
        )
        assert report.issue_count == 2

    def test_to_dict_contains_required_keys(self):
        report = PlaceholderReport(
            profile_name="prod",
            issues=[PlaceholderIssue("URL", "${HOST}")],
        )
        d = report.to_dict()
        assert d["profile"] == "prod"
        assert len(d["issues"]) == 1
        assert d["issues"][0]["var"] == "URL"
        assert d["issues"][0]["placeholder"] == "${HOST}"

    def test_repr_contains_profile_name(self):
        report = PlaceholderReport(profile_name="staging")
        assert "staging" in repr(report)


class TestPlaceholderChecker:
    def test_no_placeholders_returns_empty_report(self, checker):
        report = checker.check("dev", {"HOST": "localhost", "PORT": "5432"})
        assert not report.has_issues

    def test_detects_curly_brace_placeholder(self, checker):
        report = checker.check("dev", {"URL": "http://${HOST}:8080"})
        assert report.has_issues
        assert report.issues[0].placeholder == "${HOST}"
        assert report.issues[0].var_name == "URL"

    def test_detects_dollar_placeholder(self, checker):
        report = checker.check("dev", {"DSN": "postgres://$USER@localhost/db"})
        assert report.has_issues
        assert report.issues[0].placeholder == "$USER"

    def test_resolved_placeholder_not_flagged(self, checker):
        report = checker.check("dev", {"HOST": "localhost", "URL": "http://${HOST}"})
        assert not report.has_issues

    def test_multiple_issues_in_one_value(self, checker):
        report = checker.check("dev", {"URL": "${SCHEME}://${HOST}:${PORT}"})
        assert report.issue_count == 3

    def test_check_resolved_substitutes_known_vars(self, checker):
        variables = {"HOST": "localhost", "URL": "http://${HOST}:8080"}
        resolved = checker.check_resolved(variables)
        assert resolved["URL"] == "http://localhost:8080"

    def test_check_resolved_leaves_unknown_vars(self, checker):
        variables = {"URL": "http://${UNKNOWN}:8080"}
        resolved = checker.check_resolved(variables)
        assert "${UNKNOWN}" in resolved["URL"]

    def test_profile_name_in_report(self, checker):
        report = checker.check("my-profile", {})
        assert report.profile_name == "my-profile"
