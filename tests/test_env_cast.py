"""Tests for envchain.env_cast."""
import pytest
from envchain.env_cast import CastResult, CastReport, EnvCaster, CAST_TYPES


@pytest.fixture
def caster():
    return EnvCaster()


@pytest.fixture
def sample_vars():
    return {"PORT": "8080", "RATE": "3.14", "DEBUG": "true", "NAME": "hello"}


class TestCastResult:
    def test_repr_ok(self):
        r = CastResult(name="X", original="1", casted=1, cast_type="int", success=True)
        assert "ok" in repr(r)
        assert "X" in repr(r)
        assert "int" in repr(r)

    def test_repr_fail(self):
        r = CastResult(name="X", original="abc", casted=None, cast_type="int", success=False, error="bad")
        assert "error" in repr(r)
        assert "bad" in repr(r)


class TestCastReport:
    def test_success_count(self):
        results = [
            CastResult("A", "1", 1, "int", True),
            CastResult("B", "x", None, "int", False, error="err"),
        ]
        report = CastReport(results=results)
        assert report.success_count == 1
        assert report.failure_count == 1

    def test_has_failures_false_when_all_ok(self):
        results = [CastResult("A", "1", 1, "int", True)]
        report = CastReport(results=results)
        assert not report.has_failures

    def test_has_failures_true_when_any_fail(self):
        results = [CastResult("A", "x", None, "int", False, error="e")]
        report = CastReport(results=results)
        assert report.has_failures

    def test_to_dict_contains_required_keys(self):
        report = CastReport()
        d = report.to_dict()
        assert "success_count" in d
        assert "failure_count" in d
        assert "results" in d


class TestEnvCaster:
    def test_cast_to_int(self, caster):
        report = caster.cast({"PORT": "8080"}, "int")
        assert report.success_count == 1
        assert report.results[0].casted == 8080

    def test_cast_to_float(self, caster):
        report = caster.cast({"RATE": "3.14"}, "float")
        assert report.results[0].casted == pytest.approx(3.14)

    def test_cast_to_bool_true(self, caster):
        for val in ("1", "true", "yes", "on", "True", "YES"):
            report = caster.cast({"F": val}, "bool")
            assert report.results[0].casted is True

    def test_cast_to_bool_false(self, caster):
        for val in ("0", "false", "no", "off"):
            report = caster.cast({"F": val}, "bool")
            assert report.results[0].casted is False

    def test_cast_to_bool_invalid(self, caster):
        report = caster.cast({"F": "maybe"}, "bool")
        assert not report.results[0].success

    def test_cast_to_json(self, caster):
        report = caster.cast({"OBJ": '{"a": 1}'}, "json")
        assert report.results[0].casted == {"a": 1}

    def test_cast_to_str_always_succeeds(self, caster):
        report = caster.cast({"X": "anything"}, "str")
        assert report.success_count == 1

    def test_invalid_type_raises(self, caster):
        with pytest.raises(ValueError, match="Unknown cast type"):
            caster.cast({"X": "1"}, "bytes")

    def test_multiple_vars_partial_failure(self, caster):
        report = caster.cast({"A": "1", "B": "not_int"}, "int")
        assert report.success_count == 1
        assert report.failure_count == 1

    def test_empty_vars_returns_empty_report(self, caster):
        report = caster.cast({}, "int")
        assert report.success_count == 0
        assert report.failure_count == 0
