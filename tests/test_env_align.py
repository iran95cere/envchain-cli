"""Tests for env_align module."""
import pytest
from envchain.env_align import AlignResult, AlignReport, EnvAligner


@pytest.fixture
def aligner():
    return EnvAligner()


@pytest.fixture
def sample_vars():
    return {"KEY": "  hello  ", "CLEAN": "world", "SPACES": "  padded "}


class TestAlignResult:
    def test_changed_true_when_values_differ(self):
        r = AlignResult(name="K", original="  v  ", aligned="v")
        assert r.changed is True

    def test_changed_false_when_values_same(self):
        r = AlignResult(name="K", original="v", aligned="v")
        assert r.changed is False

    def test_repr_contains_name(self):
        r = AlignResult(name="MY_VAR", original="x", aligned="x")
        assert "MY_VAR" in repr(r)

    def test_repr_changed_status(self):
        r = AlignResult(name="K", original="  v", aligned="v")
        assert "changed" in repr(r)

    def test_repr_unchanged_status(self):
        r = AlignResult(name="K", original="v", aligned="v")
        assert "unchanged" in repr(r)


class TestAlignReport:
    def test_changed_count_zero_when_clean(self):
        report = AlignReport(results=[AlignResult("K", "v", "v")])
        assert report.changed_count == 0

    def test_changed_count_nonzero_when_dirty(self):
        report = AlignReport(results=[AlignResult("K", "  v  ", "v")])
        assert report.changed_count == 1

    def test_has_changes_false_when_clean(self):
        report = AlignReport()
        assert report.has_changes is False

    def test_has_changes_true_when_dirty(self):
        report = AlignReport(results=[AlignResult("K", "  v", "v")])
        assert report.has_changes is True

    def test_aligned_vars_returns_dict(self):
        report = AlignReport(results=[AlignResult("K", "  v  ", "v")])
        assert report.aligned_vars() == {"K": "v"}

    def test_repr_contains_counts(self):
        report = AlignReport(results=[AlignResult("K", "  v", "v")])
        assert "changed=1" in repr(report)


class TestEnvAligner:
    def test_strips_whitespace(self, aligner, sample_vars):
        report = aligner.align(sample_vars)
        aligned = report.aligned_vars()
        assert aligned["KEY"] == "hello"
        assert aligned["SPACES"] == "padded"

    def test_clean_value_unchanged(self, aligner, sample_vars):
        report = aligner.align(sample_vars)
        r = next(r for r in report.results if r.name == "CLEAN")
        assert r.changed is False

    def test_pad_width_pads_short_values(self):
        a = EnvAligner(pad_width=10)
        report = a.align({"K": "hi"})
        assert len(report.aligned_vars()["K"]) == 10

    def test_pad_width_zero_no_padding(self):
        a = EnvAligner(pad_width=0)
        report = a.align({"K": "hi"})
        assert report.aligned_vars()["K"] == "hi"

    def test_negative_pad_width_raises(self):
        with pytest.raises(ValueError):
            EnvAligner(pad_width=-1)

    def test_empty_vars_returns_empty_report(self, aligner):
        report = aligner.align({})
        assert report.changed_count == 0
        assert report.aligned_vars() == {}
