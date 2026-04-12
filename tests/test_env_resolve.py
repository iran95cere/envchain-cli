"""Tests for envchain.env_resolve."""

from __future__ import annotations

import pytest

from envchain.env_resolve import EnvResolver, ResolveIssue, ResolveResult


@pytest.fixture
def resolver() -> EnvResolver:
    return EnvResolver()


class TestResolveResult:
    def test_has_issues_false_when_empty(self):
        r = ResolveResult(resolved={"A": "1"})
        assert not r.has_issues

    def test_has_issues_true_when_present(self):
        issue = ResolveIssue(var_name="A", reference="B", reason="missing")
        r = ResolveResult(resolved={}, issues=[issue])
        assert r.has_issues

    def test_issue_count(self):
        issues = [
            ResolveIssue("A", "B", "missing"),
            ResolveIssue("C", "D", "missing"),
        ]
        r = ResolveResult(issues=issues)
        assert r.issue_count == 2

    def test_repr_contains_counts(self):
        r = ResolveResult(resolved={"X": "1"}, issues=[])
        assert "resolved=1" in repr(r)
        assert "issues=0" in repr(r)


class TestEnvResolver:
    def test_no_references_unchanged(self, resolver):
        vars = {"FOO": "bar", "BAZ": "qux"}
        result = resolver.resolve(vars)
        assert result.resolved == vars
        assert not result.has_issues

    def test_simple_reference_resolved(self, resolver):
        vars = {"BASE": "/home/user", "PATH": "${BASE}/bin"}
        result = resolver.resolve(vars)
        assert result.resolved["PATH"] == "/home/user/bin"
        assert not result.has_issues

    def test_chained_references_resolved(self, resolver):
        vars = {
            "A": "hello",
            "B": "${A}_world",
            "C": "${B}!",
        }
        result = resolver.resolve(vars)
        assert result.resolved["C"] == "hello_world!"

    def test_missing_reference_produces_issue(self, resolver):
        vars = {"FOO": "${MISSING}_value"}
        result = resolver.resolve(vars)
        assert result.has_issues
        assert result.issues[0].var_name == "FOO"
        assert result.issues[0].reference == "MISSING"
        # Original value kept
        assert result.resolved["FOO"] == "${MISSING}_value"

    def test_multiple_refs_in_one_value(self, resolver):
        vars = {"X": "a", "Y": "b", "Z": "${X}-${Y}"}
        result = resolver.resolve(vars)
        assert result.resolved["Z"] == "a-b"

    def test_self_reference_detected_as_issue(self, resolver):
        # Self-reference creates a cycle via depth limit
        vars = {"A": "${A}"}
        result = resolver.resolve(vars)
        assert result.has_issues

    def test_empty_vars_returns_empty_result(self, resolver):
        result = resolver.resolve({})
        assert result.resolved == {}
        assert not result.has_issues

    def test_issue_repr_contains_fields(self):
        issue = ResolveIssue(var_name="FOO", reference="BAR", reason="missing")
        r = repr(issue)
        assert "FOO" in r
        assert "BAR" in r
        assert "missing" in r
