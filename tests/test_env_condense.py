"""Tests for EnvCondenser and related dataclasses."""
import pytest
from envchain.env_condense import CondenseResult, CondenseReport, EnvCondenser


@pytest.fixture
def condenser():
    return EnvCondenser()


@pytest.fixture
def sample_vars():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "EMPTY_VAR": "",
        "db_host": "duplicate_lower",
        "API_KEY": "secret",
    }


class TestCondenseResult:
    def test_removed_count(self):
        r = CondenseResult(name="p", original_count=5, condensed_count=3, removed=["A", "B"])
        assert r.removed_count == 2

    def test_is_changed_true(self):
        r = CondenseResult(name="p", original_count=5, condensed_count=3)
        assert r.is_changed is True

    def test_is_changed_false(self):
        r = CondenseResult(name="p", original_count=3, condensed_count=3)
        assert r.is_changed is False

    def test_repr_contains_profile(self):
        r = CondenseResult(name="myprofile", original_count=4, condensed_count=2)
        assert "myprofile" in repr(r)

    def test_repr_contains_counts(self):
        r = CondenseResult(name="p", original_count=4, condensed_count=2)
        rep = repr(r)
        assert "4" in rep and "2" in rep


class TestCondenseReport:
    def test_changed_count_zero_when_no_changes(self):
        r1 = CondenseResult(name="a", original_count=3, condensed_count=3)
        report = CondenseReport(results=[r1])
        assert report.changed_count == 0

    def test_changed_count_counts_changed(self):
        r1 = CondenseResult(name="a", original_count=5, condensed_count=3)
        r2 = CondenseResult(name="b", original_count=2, condensed_count=2)
        report = CondenseReport(results=[r1, r2])
        assert report.changed_count == 1

    def test_total_removed(self):
        r1 = CondenseResult(name="a", original_count=5, condensed_count=3, removed=["X", "Y"])
        r2 = CondenseResult(name="b", original_count=4, condensed_count=3, removed=["Z"])
        report = CondenseReport(results=[r1, r2])
        assert report.total_removed == 3

    def test_has_changes_false_when_empty(self):
        report = CondenseReport()
        assert report.has_changes is False


class TestEnvCondenser:
    def test_removes_empty_values(self, condenser):
        vars_ = {"A": "val", "B": "", "C": "  "}
        result_vars, cr = condenser.condense("p", vars_)
        assert "B" not in result_vars
        assert "C" not in result_vars
        assert "A" in result_vars

    def test_deduplicates_case_insensitive(self, condenser):
        vars_ = {"DB_HOST": "localhost", "db_host": "other"}
        result_vars, cr = condenser.condense("p", vars_)
        assert len(result_vars) == 1
        assert "DB_HOST" in result_vars

    def test_strip_empty_false_keeps_empty(self, condenser):
        vars_ = {"A": "", "B": "val"}
        result_vars, cr = condenser.condense("p", vars_, strip_empty=False)
        assert "A" in result_vars

    def test_deduplicate_case_false_keeps_both(self, condenser):
        vars_ = {"DB_HOST": "a", "db_host": "b"}
        result_vars, cr = condenser.condense("p", vars_, deduplicate_case=False)
        assert len(result_vars) == 2

    def test_result_removed_list(self, condenser, sample_vars):
        _, cr = condenser.condense("prof", sample_vars)
        assert "EMPTY_VAR" in cr.removed or "db_host" in cr.removed

    def test_no_changes_when_all_clean(self, condenser):
        vars_ = {"A": "1", "B": "2"}
        _, cr = condenser.condense("p", vars_)
        assert not cr.is_changed
