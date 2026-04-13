"""Tests for envchain.env_sanitize."""

import pytest
from envchain.env_sanitize import EnvSanitizer, SanitizeIssue, SanitizeReport


@pytest.fixture
def sanitizer() -> EnvSanitizer:
    return EnvSanitizer()


@pytest.fixture
def nl_sanitizer() -> EnvSanitizer:
    return EnvSanitizer(strip_newlines=True)


class TestSanitizeReport:
    def test_changed_count_zero_when_clean(self, sanitizer):
        report = sanitizer.sanitize({"FOO": "bar", "BAZ": "qux"})
        assert report.changed_count == 0

    def test_has_issues_false_when_clean(self, sanitizer):
        report = sanitizer.sanitize({"FOO": "clean_value"})
        assert not report.has_issues

    def test_has_issues_true_when_dirty(self, sanitizer):
        report = sanitizer.sanitize({"FOO": "bad\x00value"})
        assert report.has_issues

    def test_changed_count_increments_per_dirty_var(self, sanitizer):
        report = sanitizer.sanitize({"A": "ok", "B": "bad\x01", "C": "also\x02bad"})
        assert report.changed_count == 2


class TestNullByteRemoval:
    def test_null_byte_stripped(self, sanitizer):
        report = sanitizer.sanitize({"KEY": "val\x00ue"})
        assert report.sanitized["KEY"] == "value"

    def test_null_byte_issue_description(self, sanitizer):
        report = sanitizer.sanitize({"KEY": "\x00"})
        assert any("null byte" in i.description for i in report.issues)

    def test_null_byte_replacement_char(self):
        s = EnvSanitizer(replacement="?")
        report = s.sanitize({"K": "a\x00b"})
        assert report.sanitized["K"] == "a?b"


class TestControlCharRemoval:
    def test_control_char_stripped(self, sanitizer):
        report = sanitizer.sanitize({"K": "hello\x07world"})
        assert report.sanitized["K"] == "helloworld"

    def test_control_char_issue_description(self, sanitizer):
        report = sanitizer.sanitize({"K": "\x1b[31m"})
        assert any("control characters" in i.description for i in report.issues)

    def test_tab_not_stripped(self, sanitizer):
        """Tab (0x09) is a valid whitespace character and should not be removed."""
        report = sanitizer.sanitize({"K": "col1\tcol2"})
        assert report.sanitized["K"] == "col1\tcol2"
        assert not report.has_issues


class TestNewlineHandling:
    def test_newlines_kept_by_default(self, sanitizer):
        report = sanitizer.sanitize({"K": "line1\nline2"})
        assert "\n" in report.sanitized["K"]
        assert not report.has_issues

    def test_newlines_stripped_when_option_set(self, nl_sanitizer):
        report = nl_sanitizer.sanitize({"K": "line1\nline2"})
        assert "\n" not in report.sanitized["K"]

    def test_newline_issue_recorded(self, nl_sanitizer):
        report = nl_sanitizer.sanitize({"K": "a\nb"})
        assert any("newlines" in i.description for i in report.issues)


class TestOriginalPreserved:
    def test_original_dict_unchanged(self, sanitizer):
        vars_ = {"K": "bad\x00val"}
        report = sanitizer.sanitize(vars_)
        assert report.original["K"] == "bad\x00val"
        assert vars_["K"] == "bad\x00val"  # input not mutated

    def test_issue_var_name_matches(self, sanitizer):
        report = sanitizer.sanitize({"MY_VAR": "\x01"})
        assert report.issues[0].var_name == "MY_VAR"
