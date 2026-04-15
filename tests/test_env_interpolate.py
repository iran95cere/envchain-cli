"""Tests for EnvInterpolator."""
import pytest
from envchain.env_interpolate import EnvInterpolator, InterpolateReport, InterpolateResult


@pytest.fixture
def interpolator() -> EnvInterpolator:
    return EnvInterpolator()


@pytest.fixture
def sample_vars() -> dict:
    return {
        "BASE": "/home/user",
        "CONF": "${BASE}/.config",
        "LOG": "${CONF}/logs",
        "PLAIN": "no-refs-here",
    }


class TestInterpolateResult:
    def test_changed_true_when_values_differ(self):
        r = InterpolateResult(name="X", original="${Y}", resolved="hello", refs=["Y"])
        assert r.changed is True

    def test_changed_false_when_values_same(self):
        r = InterpolateResult(name="X", original="plain", resolved="plain")
        assert r.changed is False


class TestInterpolateReport:
    def test_changed_count_zero_when_no_changes(self):
        report = InterpolateReport(results=[
            InterpolateResult("A", "v", "v"),
        ])
        assert report.changed_count == 0

    def test_changed_count_counts_changed(self):
        report = InterpolateReport(results=[
            InterpolateResult("A", "${X}", "hello", refs=["X"]),
            InterpolateResult("B", "plain", "plain"),
        ])
        assert report.changed_count == 1

    def test_has_unresolved_false_when_empty(self):
        report = InterpolateReport()
        assert report.has_unresolved is False

    def test_has_unresolved_true_when_present(self):
        report = InterpolateReport(unresolved=["MISSING"])
        assert report.has_unresolved is True


class TestEnvInterpolator:
    def test_simple_reference_resolved(self, interpolator):
        report = interpolator.interpolate({"BASE": "/tmp", "DIR": "${BASE}/logs"})
        resolved = {r.name: r.resolved for r in report.results}
        assert resolved["DIR"] == "/tmp/logs"

    def test_chained_references_resolved(self, interpolator, sample_vars):
        report = interpolator.interpolate(sample_vars)
        resolved = {r.name: r.resolved for r in report.results}
        assert resolved["CONF"] == "/home/user/.config"
        assert resolved["LOG"] == "/home/user/.config/logs"

    def test_plain_value_unchanged(self, interpolator, sample_vars):
        report = interpolator.interpolate(sample_vars)
        plain = next(r for r in report.results if r.name == "PLAIN")
        assert plain.changed is False
        assert plain.resolved == "no-refs-here"

    def test_missing_ref_recorded_in_unresolved(self, interpolator):
        report = interpolator.interpolate({"A": "${MISSING}"})
        assert "MISSING" in report.unresolved

    def test_missing_ref_strict_raises(self, interpolator):
        with pytest.raises(ValueError, match="MISSING"):
            interpolator.interpolate({"A": "${MISSING}"}, strict=True)

    def test_refs_list_populated(self, interpolator):
        report = interpolator.interpolate({"BASE": "x", "DIR": "${BASE}/y"})
        dir_result = next(r for r in report.results if r.name == "DIR")
        assert "BASE" in dir_result.refs

    def test_no_refs_gives_empty_refs_list(self, interpolator):
        report = interpolator.interpolate({"PLAIN": "value"})
        plain = report.results[0]
        assert plain.refs == []

    def test_self_reference_does_not_loop(self, interpolator):
        # Self-reference: cannot resolve, should not hang
        report = interpolator.interpolate({"A": "${A}"})
        assert "A" in report.unresolved
