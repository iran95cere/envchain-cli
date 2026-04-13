"""Tests for envchain.env_regex."""

import pytest
from envchain.env_regex import EnvRegex, RegexMatch, RegexReport


@pytest.fixture
def regex():
    return EnvRegex()


SAMPLE = {
    "DATABASE_URL": "postgres://localhost/db",
    "SECRET_KEY": "s3cr3t",
    "APP_DEBUG": "true",
    "AWS_ACCESS_KEY_ID": "AKIA123",
}


class TestRegexMatch:
    def test_repr_contains_name_and_pattern(self):
        m = RegexMatch(name="FOO", value="bar", pattern="F.*")
        assert "FOO" in repr(m)
        assert "F.*" in repr(m)

    def test_to_dict_contains_required_keys(self):
        m = RegexMatch(name="FOO", value="bar", pattern="F.*")
        d = m.to_dict()
        assert d["name"] == "FOO"
        assert d["value"] == "bar"
        assert d["pattern"] == "F.*"


class TestRegexReport:
    def test_match_count_zero_when_empty(self):
        r = RegexReport()
        assert r.match_count == 0

    def test_has_errors_false_when_clean(self):
        r = RegexReport()
        assert not r.has_errors

    def test_repr_contains_counts(self):
        r = RegexReport(matches=[RegexMatch("A", "v", "p")], errors=["e"])
        assert "1" in repr(r)


class TestMatchByName:
    def test_returns_matching_names(self, regex):
        report = regex.match_by_name(SAMPLE, r"^AWS_")
        assert report.match_count == 1
        assert report.matches[0].name == "AWS_ACCESS_KEY_ID"

    def test_case_insensitive_flag(self, regex):
        import re
        report = regex.match_by_name(SAMPLE, r"secret", flags=re.IGNORECASE)
        assert any(m.name == "SECRET_KEY" for m in report.matches)

    def test_no_matches_returns_empty(self, regex):
        report = regex.match_by_name(SAMPLE, r"^NONEXISTENT")
        assert report.match_count == 0

    def test_invalid_pattern_returns_error(self, regex):
        report = regex.match_by_name(SAMPLE, r"[invalid")
        assert report.has_errors
        assert report.match_count == 0


class TestMatchByValue:
    def test_returns_matching_values(self, regex):
        report = regex.match_by_value(SAMPLE, r"localhost")
        assert report.match_count == 1
        assert report.matches[0].name == "DATABASE_URL"

    def test_matches_multiple(self, regex):
        report = regex.match_by_value(SAMPLE, r"^[A-Z]")
        assert report.match_count >= 1

    def test_invalid_pattern_returns_error(self, regex):
        report = regex.match_by_value(SAMPLE, r"(unclosed")
        assert report.has_errors


class TestValidatePattern:
    def test_valid_pattern_returns_none(self, regex):
        assert regex.validate_pattern(r"^FOO_\w+$") is None

    def test_invalid_pattern_returns_string(self, regex):
        result = regex.validate_pattern(r"[bad")
        assert isinstance(result, str)
        assert len(result) > 0
