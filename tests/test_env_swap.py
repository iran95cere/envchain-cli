"""Tests for envchain.env_swap."""
import pytest
from envchain.env_swap import EnvSwapper, SwapResult, SwapReport


@pytest.fixture
def swapper():
    return EnvSwapper()


@pytest.fixture
def sample_vars():
    return {"FOO": "foo_val", "BAR": "bar_val", "BAZ": "baz_val"}


class TestSwapResult:
    def test_repr_success(self):
        r = SwapResult(var_a="A", var_b="B", value_a="x", value_b="y")
        assert "A" in repr(r)
        assert "B" in repr(r)
        assert "ok" in repr(r)

    def test_repr_failure(self):
        r = SwapResult(var_a="A", var_b="B", value_a="", value_b="",
                       success=False, error="not found")
        assert "error" in repr(r)


class TestSwapReport:
    def test_success_count(self):
        r1 = SwapResult("A", "B", "a", "b", success=True)
        r2 = SwapResult("C", "D", "", "", success=False, error="missing")
        report = SwapReport(results=[r1, r2])
        assert report.success_count == 1

    def test_failure_count(self):
        r1 = SwapResult("A", "B", "", "", success=False, error="x")
        report = SwapReport(results=[r1])
        assert report.failure_count == 1

    def test_has_failures_false_when_all_ok(self):
        r = SwapResult("A", "B", "a", "b")
        report = SwapReport(results=[r])
        assert not report.has_failures

    def test_has_failures_true_when_any_fail(self):
        r = SwapResult("A", "B", "", "", success=False, error="x")
        report = SwapReport(results=[r])
        assert report.has_failures

    def test_repr_contains_counts(self):
        report = SwapReport()
        assert "swaps=0" in repr(report)


class TestEnvSwapper:
    def test_swap_exchanges_values(self, swapper, sample_vars):
        result = swapper.swap(sample_vars, "FOO", "BAR")
        assert result.success
        assert sample_vars["FOO"] == "bar_val"
        assert sample_vars["BAR"] == "foo_val"

    def test_swap_result_stores_original_values(self, swapper, sample_vars):
        result = swapper.swap(sample_vars, "FOO", "BAR")
        assert result.value_a == "foo_val"
        assert result.value_b == "bar_val"

    def test_swap_missing_var_a_returns_failure(self, swapper, sample_vars):
        result = swapper.swap(sample_vars, "MISSING", "BAR")
        assert not result.success
        assert "MISSING" in result.error

    def test_swap_missing_var_b_returns_failure(self, swapper, sample_vars):
        result = swapper.swap(sample_vars, "FOO", "MISSING")
        assert not result.success
        assert "MISSING" in result.error

    def test_swap_does_not_mutate_on_failure(self, swapper, sample_vars):
        original_foo = sample_vars["FOO"]
        swapper.swap(sample_vars, "FOO", "MISSING")
        assert sample_vars["FOO"] == original_foo

    def test_swap_many_all_success(self, swapper, sample_vars):
        report = swapper.swap_many(sample_vars, [("FOO", "BAR"), ("BAR", "BAZ")])
        assert report.success_count == 2
        assert not report.has_failures

    def test_swap_many_partial_failure(self, swapper, sample_vars):
        report = swapper.swap_many(sample_vars, [("FOO", "BAR"), ("X", "Y")])
        assert report.success_count == 1
        assert report.failure_count == 1

    def test_swap_many_empty_pairs(self, swapper, sample_vars):
        report = swapper.swap_many(sample_vars, [])
        assert report.success_count == 0
        assert not report.has_failures
