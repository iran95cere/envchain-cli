"""Tests for EnvTypeChecker and TypeCheckReport."""
import pytest
from envchain.env_typecheck import (
    EnvTypeChecker,
    TypeCheckReport,
    TypeCheckResult,
    VarType,
)


@pytest.fixture
def checker():
    return EnvTypeChecker()


# --- TypeCheckResult ---

class TestTypeCheckResult:
    def test_repr_ok(self):
        r = TypeCheckResult("PORT", "8080", VarType.INTEGER, True)
        assert "OK" in repr(r)
        assert "PORT" in repr(r)

    def test_repr_fail(self):
        r = TypeCheckResult("PORT", "abc", VarType.INTEGER, False, "bad")
        assert "FAIL" in repr(r)


# --- TypeCheckReport ---

class TestTypeCheckReport:
    def test_has_failures_false_when_empty(self):
        report = TypeCheckReport()
        assert not report.has_failures

    def test_passed_count(self):
        results = [
            TypeCheckResult("A", "1", VarType.INTEGER, True),
            TypeCheckResult("B", "x", VarType.INTEGER, False),
        ]
        report = TypeCheckReport(results=results)
        assert report.passed_count == 1
        assert report.failed_count == 1

    def test_failures_returns_only_failed(self):
        results = [
            TypeCheckResult("A", "1", VarType.INTEGER, True),
            TypeCheckResult("B", "x", VarType.INTEGER, False),
        ]
        report = TypeCheckReport(results=results)
        assert len(report.failures()) == 1
        assert report.failures()[0].name == "B"

    def test_repr_contains_counts(self):
        report = TypeCheckReport()
        assert "total=0" in repr(report)


# --- EnvTypeChecker ---

class TestEnvTypeChecker:
    def test_string_always_passes(self, checker):
        r = checker.check("X", "anything", VarType.STRING)
        assert r.passed

    def test_valid_integer(self, checker):
        assert checker.check("PORT", "8080", VarType.INTEGER).passed

    def test_invalid_integer(self, checker):
        r = checker.check("PORT", "abc", VarType.INTEGER)
        assert not r.passed
        assert r.message != ""

    def test_valid_float(self, checker):
        assert checker.check("RATIO", "3.14", VarType.FLOAT).passed

    def test_invalid_float(self, checker):
        assert not checker.check("RATIO", "three", VarType.FLOAT).passed

    def test_valid_boolean(self, checker):
        for val in ("true", "false", "1", "0", "yes", "no", "True", "YES"):
            assert checker.check("FLAG", val, VarType.BOOLEAN).passed, val

    def test_invalid_boolean(self, checker):
        assert not checker.check("FLAG", "maybe", VarType.BOOLEAN).passed

    def test_valid_url(self, checker):
        assert checker.check("ENDPOINT", "https://example.com/path", VarType.URL).passed

    def test_invalid_url(self, checker):
        assert not checker.check("ENDPOINT", "not-a-url", VarType.URL).passed

    def test_valid_email(self, checker):
        assert checker.check("MAIL", "user@example.com", VarType.EMAIL).passed

    def test_invalid_email(self, checker):
        assert not checker.check("MAIL", "notanemail", VarType.EMAIL).passed

    def test_check_all_returns_report(self, checker):
        schema = {"PORT": VarType.INTEGER, "HOST": VarType.STRING}
        report = checker.check_all({"PORT": "9000", "HOST": "localhost"}, schema)
        assert report.passed_count == 2
        assert not report.has_failures

    def test_check_all_missing_var_uses_empty_string(self, checker):
        schema = {"PORT": VarType.INTEGER}
        report = checker.check_all({}, schema)
        assert report.failed_count == 1
