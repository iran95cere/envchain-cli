"""Tests for envchain.env_truncate."""

import pytest
from envchain.env_truncate import EnvTruncator, TruncateResult, TruncateReport


@pytest.fixture
def truncator():
    return EnvTruncator(max_length=10, suffix="...")


@pytest.fixture
def sample_vars():
    return {
        "SHORT": "hi",
        "EXACT": "1234567890",
        "LONG": "this is a very long value that exceeds the limit",
    }


class TestTruncateResult:
    def test_changed_true_when_values_differ(self):
        r = TruncateResult(name="X", original="hello world", truncated="hello w...", max_length=10)
        assert r.changed is True

    def test_changed_false_when_values_same(self):
        r = TruncateResult(name="X", original="hi", truncated="hi", max_length=10)
        assert r.changed is False

    def test_repr_truncated(self):
        r = TruncateResult(name="X", original="hello world", truncated="hello w...", max_length=10)
        assert "truncated" in repr(r)
        assert "X" in repr(r)

    def test_repr_unchanged(self):
        r = TruncateResult(name="Y", original="ok", truncated="ok", max_length=10)
        assert "unchanged" in repr(r)


class TestTruncateReport:
    def test_changed_count_zero_when_no_changes(self):
        results = [
            TruncateResult("A", "hi", "hi", 10),
            TruncateResult("B", "ok", "ok", 10),
        ]
        report = TruncateReport(results=results)
        assert report.changed_count == 0

    def test_changed_count_correct(self):
        results = [
            TruncateResult("A", "hi", "hi", 10),
            TruncateResult("B", "hello world!", "hello w...", 10),
        ]
        report = TruncateReport(results=results)
        assert report.changed_count == 1

    def test_has_changes_false_when_empty(self):
        report = TruncateReport()
        assert report.has_changes is False

    def test_has_changes_true(self):
        results = [TruncateResult("A", "long value here", "long va...", 10)]
        report = TruncateReport(results=results)
        assert report.has_changes is True

    def test_to_dict_contains_required_keys(self):
        report = TruncateReport()
        d = report.to_dict()
        assert "changed_count" in d
        assert "total" in d
        assert "results" in d


class TestEnvTruncator:
    def test_short_value_unchanged(self, truncator):
        result = truncator.truncate_value("hi")
        assert result == "hi"

    def test_exact_length_unchanged(self, truncator):
        result = truncator.truncate_value("1234567890")
        assert result == "1234567890"

    def test_long_value_truncated_with_suffix(self, truncator):
        result = truncator.truncate_value("hello world!")
        assert result == "hello w..."
        assert len(result) == 10

    def test_truncate_returns_report(self, truncator, sample_vars):
        report = truncator.truncate(sample_vars)
        assert isinstance(report, TruncateReport)
        assert len(report.results) == len(sample_vars)

    def test_apply_returns_dict(self, truncator, sample_vars):
        result = truncator.apply(sample_vars)
        assert isinstance(result, dict)
        assert set(result.keys()) == set(sample_vars.keys())

    def test_apply_truncates_long_values(self, truncator):
        result = truncator.apply({"K": "this is way too long"})
        assert len(result["K"]) <= 10
        assert result["K"].endswith("...")

    def test_invalid_max_length_raises(self):
        with pytest.raises(ValueError):
            EnvTruncator(max_length=2, suffix="...")

    def test_default_max_length(self):
        t = EnvTruncator()
        assert t.max_length == EnvTruncator.DEFAULT_MAX_LENGTH
