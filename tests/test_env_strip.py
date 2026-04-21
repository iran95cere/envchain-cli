"""Tests for envchain.env_strip."""
import pytest
from envchain.env_strip import EnvStripper, StripResult, StripReport


@pytest.fixture
def stripper():
    return EnvStripper()


@pytest.fixture
def sample_vars():
    return {
        "HOST": "  localhost  ",
        "PORT": "8080",
        "PATH": "  /usr/bin  ",
        "CLEAN": "already_clean",
    }


class TestStripResult:
    def test_changed_true_when_values_differ(self):
        r = StripResult(name="X", original="  hi  ", stripped="hi", chars=None)
        assert r.changed is True

    def test_changed_false_when_values_same(self):
        r = StripResult(name="X", original="hi", stripped="hi", chars=None)
        assert r.changed is False

    def test_repr_changed(self):
        r = StripResult(name="X", original="  hi  ", stripped="hi", chars=None)
        assert "->" in repr(r)
        assert "X" in repr(r)

    def test_repr_unchanged(self):
        r = StripResult(name="X", original="hi", stripped="hi", chars=None)
        assert "unchanged" in repr(r)


class TestStripReport:
    def test_changed_count_zero_when_clean(self, stripper):
        report = stripper.strip({"A": "clean", "B": "also_clean"})
        assert report.changed_count == 0

    def test_has_changes_false_when_clean(self, stripper):
        report = stripper.strip({"A": "clean"})
        assert report.has_changes is False

    def test_has_changes_true_when_dirty(self, stripper):
        report = stripper.strip({"A": "  dirty  "})
        assert report.has_changes is True

    def test_changed_count_matches_dirty_vars(self, stripper, sample_vars):
        report = stripper.strip(sample_vars)
        assert report.changed_count == 2  # HOST and PATH

    def test_to_dict_contains_required_keys(self, stripper, sample_vars):
        report = stripper.strip(sample_vars)
        d = report.to_dict()
        assert "changed_count" in d
        assert "total" in d
        assert "results" in d

    def test_to_dict_total_matches_input(self, stripper, sample_vars):
        report = stripper.strip(sample_vars)
        assert report.to_dict()["total"] == len(sample_vars)

    def test_repr_contains_counts(self, stripper, sample_vars):
        report = stripper.strip(sample_vars)
        assert "StripReport" in repr(report)


class TestEnvStripper:
    def test_strip_whitespace_default(self, stripper):
        report = stripper.strip({"A": "  hello  "})
        assert report.results[0].stripped == "hello"

    def test_strip_custom_chars(self, stripper):
        report = stripper.strip({"A": "***value***"}, chars="*")
        assert report.results[0].stripped == "value"

    def test_strip_no_change_when_already_clean(self, stripper):
        report = stripper.strip({"A": "clean"})
        assert not report.results[0].changed

    def test_apply_returns_dict(self, stripper, sample_vars):
        result = stripper.apply(sample_vars)
        assert isinstance(result, dict)
        assert result["HOST"] == "localhost"
        assert result["PORT"] == "8080"

    def test_apply_preserves_unchanged_values(self, stripper):
        result = stripper.apply({"A": "no_change"})
        assert result["A"] == "no_change"

    def test_strip_empty_string_unchanged(self, stripper):
        report = stripper.strip({"EMPTY": ""})
        assert not report.results[0].changed

    def test_strip_only_spaces_becomes_empty(self, stripper):
        report = stripper.strip({"SPACES": "   "})
        assert report.results[0].stripped == ""
        assert report.results[0].changed
