"""Tests for envchain.env_shrink."""
import pytest
from envchain.env_shrink import EnvShrinker, ShrinkResult, ShrinkReport


@pytest.fixture
def shrinker():
    return EnvShrinker(strategy="strip")


@pytest.fixture
def sample_vars():
    return {
        "KEY_A": "  hello  ",
        "KEY_B": "world",
        "KEY_C": "  ",
    }


class TestShrinkResult:
    def test_changed_true_when_values_differ(self):
        r = ShrinkResult(name="X", original="  hi  ", shrunk="hi", strategy="strip")
        assert r.changed is True

    def test_changed_false_when_values_same(self):
        r = ShrinkResult(name="X", original="hi", shrunk="hi", strategy="strip")
        assert r.changed is False

    def test_saved_bytes_positive(self):
        r = ShrinkResult(name="X", original="  hi  ", shrunk="hi", strategy="strip")
        assert r.saved_bytes == 4

    def test_saved_bytes_zero_when_unchanged(self):
        r = ShrinkResult(name="X", original="hi", shrunk="hi", strategy="strip")
        assert r.saved_bytes == 0

    def test_repr_contains_name_and_strategy(self):
        r = ShrinkResult(name="X", original="  hi  ", shrunk="hi", strategy="strip")
        assert "X" in repr(r)
        assert "strip" in repr(r)


class TestShrinkReport:
    def test_changed_count_zero_when_no_changes(self):
        results = [
            ShrinkResult(name="A", original="hi", shrunk="hi", strategy="strip")
        ]
        report = ShrinkReport(results=results)
        assert report.changed_count == 0

    def test_changed_count_correct(self, shrinker, sample_vars):
        report = shrinker.shrink(sample_vars)
        assert report.changed_count == 2  # KEY_A and KEY_C

    def test_has_changes_false_when_all_clean(self):
        results = [
            ShrinkResult(name="A", original="ok", shrunk="ok", strategy="strip")
        ]
        report = ShrinkReport(results=results)
        assert report.has_changes is False

    def test_has_changes_true_when_some_changed(self, shrinker, sample_vars):
        report = shrinker.shrink(sample_vars)
        assert report.has_changes is True

    def test_total_saved_bytes(self, shrinker, sample_vars):
        report = shrinker.shrink(sample_vars)
        assert report.total_saved_bytes > 0

    def test_repr_contains_counts(self, shrinker, sample_vars):
        report = shrinker.shrink(sample_vars)
        assert "changed=" in repr(report)
        assert "saved=" in repr(report)


class TestEnvShrinker:
    def test_unknown_strategy_raises(self):
        with pytest.raises(ValueError, match="Unknown strategy"):
            EnvShrinker(strategy="nonexistent")

    def test_strip_removes_whitespace(self):
        s = EnvShrinker(strategy="strip")
        report = s.shrink({"K": "  val  "})
        assert report.results[0].shrunk == "val"

    def test_collapse_whitespace(self):
        s = EnvShrinker(strategy="collapse_whitespace")
        report = s.shrink({"K": "foo   bar"})
        assert report.results[0].shrunk == "foo bar"

    def test_lowercase_booleans_true(self):
        s = EnvShrinker(strategy="lowercase_booleans")
        report = s.shrink({"K": "TRUE"})
        assert report.results[0].shrunk == "true"

    def test_lowercase_booleans_leaves_other_values(self):
        s = EnvShrinker(strategy="lowercase_booleans")
        report = s.shrink({"K": "MyValue"})
        assert report.results[0].shrunk == "MyValue"

    def test_to_dict_returns_shrunk_values(self, shrinker, sample_vars):
        report = shrinker.shrink(sample_vars)
        result = shrinker.to_dict(report)
        assert result["KEY_A"] == "hello"
        assert result["KEY_B"] == "world"
