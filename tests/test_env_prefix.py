"""Tests for envchain.env_prefix."""
import pytest
from envchain.env_prefix import EnvPrefixer, PrefixReport, PrefixResult


@pytest.fixture
def prefixer():
    return EnvPrefixer()


@pytest.fixture
def sample_vars():
    return {"DATABASE_URL": "postgres://", "APP_SECRET": "abc", "PORT": "8080"}


class TestPrefixResult:
    def test_repr_changed(self):
        r = PrefixResult(name="PORT", original="PORT", transformed="APP_PORT", changed=True)
        assert "changed" in repr(r)
        assert "PORT" in repr(r)

    def test_repr_unchanged(self):
        r = PrefixResult(name="PORT", original="PORT", transformed="PORT", changed=False)
        assert "unchanged" in repr(r)


class TestPrefixReport:
    def test_changed_count_zero_when_no_changes(self):
        report = PrefixReport(results=[
            PrefixResult("A", "A", "A", False),
            PrefixResult("B", "B", "B", False),
        ])
        assert report.changed_count == 0

    def test_changed_count_nonzero_when_changes(self):
        report = PrefixReport(results=[
            PrefixResult("A", "A", "PRE_A", True),
            PrefixResult("B", "B", "B", False),
        ])
        assert report.changed_count == 1

    def test_has_changes_false_when_empty(self):
        assert not PrefixReport().has_changes

    def test_has_changes_true_when_changed(self):
        report = PrefixReport(results=[PrefixResult("X", "X", "PRE_X", True)])
        assert report.has_changes

    def test_to_dict_contains_required_keys(self):
        report = PrefixReport(results=[PrefixResult("X", "X", "PRE_X", True)])
        d = report.to_dict()
        assert "changed_count" in d
        assert "total" in d
        assert "results" in d


class TestEnvPrefixer:
    def test_add_prefix_renames_unprefixed_vars(self, prefixer, sample_vars):
        report = prefixer.add_prefix(sample_vars, "MY_")
        names = {r.transformed for r in report.results}
        assert "MY_PORT" in names
        assert "MY_DATABASE_URL" in names

    def test_add_prefix_skips_already_prefixed(self, prefixer):
        vars_ = {"APP_KEY": "val"}
        report = prefixer.add_prefix(vars_, "APP_")
        result = report.results[0]
        assert not result.changed
        assert result.transformed == "APP_KEY"

    def test_add_prefix_empty_raises(self, prefixer, sample_vars):
        with pytest.raises(ValueError):
            prefixer.add_prefix(sample_vars, "")

    def test_remove_prefix_strips_matching(self, prefixer):
        vars_ = {"APP_SECRET": "x", "APP_PORT": "80"}
        report = prefixer.remove_prefix(vars_, "APP_")
        assert all(r.changed for r in report.results)
        transformed = {r.transformed for r in report.results}
        assert "SECRET" in transformed
        assert "PORT" in transformed

    def test_remove_prefix_leaves_non_matching(self, prefixer, sample_vars):
        report = prefixer.remove_prefix(sample_vars, "ZZZZ_")
        assert not report.has_changes

    def test_remove_prefix_empty_raises(self, prefixer, sample_vars):
        with pytest.raises(ValueError):
            prefixer.remove_prefix(sample_vars, "")

    def test_apply_produces_correct_dict(self, prefixer, sample_vars):
        report = prefixer.add_prefix(sample_vars, "TEST_")
        result = prefixer.apply(sample_vars, report)
        assert "TEST_PORT" in result
        assert result["TEST_PORT"] == "8080"
        assert "PORT" not in result
