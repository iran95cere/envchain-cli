"""Tests for envchain.env_redact."""
import pytest
from envchain.env_redact import EnvRedactor, RedactReport, RedactResult


@pytest.fixture
def redactor() -> EnvRedactor:
    return EnvRedactor()


class TestRedactResult:
    def test_repr_redacted(self):
        r = RedactResult(name="API_KEY", original="s3cr3t", redacted="***REDACTED***", was_redacted=True)
        assert "redacted" in repr(r)
        assert "API_KEY" in repr(r)

    def test_repr_plain(self):
        r = RedactResult(name="HOST", original="localhost", redacted="localhost", was_redacted=False)
        assert "plain" in repr(r)


class TestRedactReport:
    def test_redacted_count_zero_when_no_sensitive(self, redactor):
        report = redactor.redact_all({"HOST": "localhost", "PORT": "5432"})
        assert report.redacted_count == 0

    def test_has_redacted_false_when_clean(self, redactor):
        report = redactor.redact_all({"HOST": "localhost"})
        assert not report.has_redacted

    def test_has_redacted_true_when_sensitive(self, redactor):
        report = redactor.redact_all({"DB_PASSWORD": "hunter2"})
        assert report.has_redacted

    def test_redacted_count_correct(self, redactor):
        report = redactor.redact_all({
            "DB_PASSWORD": "secret",
            "API_TOKEN": "abc123",
            "HOST": "example.com",
        })
        assert report.redacted_count == 2

    def test_to_dict_replaces_sensitive_values(self, redactor):
        report = redactor.redact_all({"DB_PASSWORD": "hunter2", "HOST": "localhost"})
        d = report.to_dict()
        assert d["DB_PASSWORD"] == EnvRedactor.PLACEHOLDER
        assert d["HOST"] == "localhost"

    def test_repr_contains_counts(self, redactor):
        report = redactor.redact_all({"SECRET": "x", "HOST": "y"})
        r = repr(report)
        assert "total=" in r
        assert "redacted=" in r


class TestIsSensitive:
    def test_password_is_sensitive(self, redactor):
        assert redactor.is_sensitive("DB_PASSWORD")

    def test_token_is_sensitive(self, redactor):
        assert redactor.is_sensitive("GITHUB_TOKEN")

    def test_api_key_is_sensitive(self, redactor):
        assert redactor.is_sensitive("STRIPE_API_KEY")

    def test_host_is_not_sensitive(self, redactor):
        assert not redactor.is_sensitive("HOST")

    def test_case_insensitive_match(self, redactor):
        assert redactor.is_sensitive("db_password")
        assert redactor.is_sensitive("DbPassword")


class TestCustomPatterns:
    def test_custom_pattern_matches(self):
        r = EnvRedactor(patterns=[r"(?i)internal"])
        assert r.is_sensitive("INTERNAL_URL")
        assert not r.is_sensitive("API_KEY")  # default not applied

    def test_custom_placeholder(self):
        r = EnvRedactor(placeholder="<hidden>")
        result = r.redact_value("DB_PASSWORD", "secret")
        assert result.redacted == "<hidden>"

    def test_empty_vars_returns_empty_report(self, redactor):
        report = redactor.redact_all({})
        assert report.redacted_count == 0
        assert report.to_dict() == {}
