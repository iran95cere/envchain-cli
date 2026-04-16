"""Tests for envchain.env_count."""
import pytest
from envchain.env_count import CountResult, CountReport, EnvCounter


@pytest.fixture
def counter():
    return EnvCounter()


@pytest.fixture
def sample_vars():
    return {"HOST": "localhost", "PORT": "8080", "SECRET": "", "TOKEN": "  "}


class TestCountResult:
    def test_to_dict_contains_required_keys(self):
        r = CountResult(profile="dev", total=4, empty=1, non_empty=3)
        d = r.to_dict()
        assert set(d.keys()) == {"profile", "total", "empty", "non_empty"}

    def test_from_dict_roundtrip(self):
        r = CountResult(profile="prod", total=10, empty=2, non_empty=8)
        assert CountResult.from_dict(r.to_dict()) == r

    def test_repr_contains_profile(self):
        r = CountResult(profile="staging", total=3, empty=0, non_empty=3)
        assert "staging" in repr(r)

    def test_repr_contains_counts(self):
        r = CountResult(profile="dev", total=5, empty=2, non_empty=3)
        assert "5" in repr(r)
        assert "2" in repr(r)


class TestEnvCounter:
    def test_count_profile_total(self, counter, sample_vars):
        result = counter.count_profile("dev", sample_vars)
        assert result.total == 4

    def test_count_profile_empty_includes_whitespace_only(self, counter, sample_vars):
        result = counter.count_profile("dev", sample_vars)
        assert result.empty == 2  # "" and "  "

    def test_count_profile_non_empty(self, counter, sample_vars):
        result = counter.count_profile("dev", sample_vars)
        assert result.non_empty == 2

    def test_count_empty_profile(self, counter):
        result = counter.count_profile("empty", {})
        assert result.total == 0
        assert result.empty == 0
        assert result.non_empty == 0

    def test_count_all_returns_report(self, counter, sample_vars):
        profiles = {"dev": sample_vars, "prod": {"HOST": "example.com"}}
        report = counter.count_all(profiles)
        assert report.total_profiles == 2

    def test_count_all_grand_total(self, counter, sample_vars):
        profiles = {"dev": sample_vars, "prod": {"HOST": "example.com"}}
        report = counter.count_all(profiles)
        assert report.grand_total == 5

    def test_count_all_empty_input(self, counter):
        report = counter.count_all({})
        assert report.total_profiles == 0
        assert report.grand_total == 0


class TestCountReport:
    def test_repr_contains_profiles_and_total(self):
        report = CountReport(results=[
            CountResult("a", 3, 1, 2),
            CountResult("b", 5, 0, 5),
        ])
        assert "2" in repr(report)   # total_profiles
        assert "8" in repr(report)   # grand_total
