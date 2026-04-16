"""Tests for envchain.env_unique."""
import pytest
from envchain.env_unique import UniqueEntry, UniqueReport, EnvUniqueness


@pytest.fixture
def analyser():
    return EnvUniqueness()


@pytest.fixture
def sample_profiles():
    return {
        "dev": {"DB_HOST": "localhost", "DEBUG": "true", "SECRET": "abc"},
        "prod": {"DB_HOST": "prod-db", "LOG_LEVEL": "warn"},
    }


class TestUniqueEntry:
    def test_to_dict_contains_required_keys(self):
        e = UniqueEntry(var_name="FOO", profiles=["dev"])
        d = e.to_dict()
        assert "var_name" in d
        assert "profiles" in d

    def test_from_dict_roundtrip(self):
        e = UniqueEntry(var_name="BAR", profiles=["dev", "prod"])
        assert UniqueEntry.from_dict(e.to_dict()).var_name == "BAR"
        assert UniqueEntry.from_dict(e.to_dict()).profiles == ["dev", "prod"]

    def test_from_dict_missing_profiles_defaults_empty(self):
        e = UniqueEntry.from_dict({"var_name": "X"})
        assert e.profiles == []

    def test_is_unique_true_when_one_profile(self):
        e = UniqueEntry(var_name="X", profiles=["dev"])
        assert e.is_unique is True

    def test_is_unique_false_when_multiple_profiles(self):
        e = UniqueEntry(var_name="X", profiles=["dev", "prod"])
        assert e.is_unique is False

    def test_repr_contains_var_name(self):
        e = UniqueEntry(var_name="MY_VAR", profiles=["dev"])
        assert "MY_VAR" in repr(e)


class TestEnvUniqueness:
    def test_shared_var_appears_in_shared_vars(self, analyser, sample_profiles):
        report = analyser.analyse(sample_profiles)
        shared_names = [e.var_name for e in report.shared_vars]
        assert "DB_HOST" in shared_names

    def test_unique_var_appears_in_unique_vars(self, analyser, sample_profiles):
        report = analyser.analyse(sample_profiles)
        unique_names = [e.var_name for e in report.unique_vars]
        assert "DEBUG" in unique_names
        assert "SECRET" in unique_names
        assert "LOG_LEVEL" in unique_names

    def test_unique_count(self, analyser, sample_profiles):
        report = analyser.analyse(sample_profiles)
        assert report.unique_count == 3

    def test_shared_count(self, analyser, sample_profiles):
        report = analyser.analyse(sample_profiles)
        assert report.shared_count == 1

    def test_empty_profiles_returns_empty_report(self, analyser):
        report = analyser.analyse({})
        assert report.entries == []

    def test_single_profile_all_unique(self, analyser):
        report = analyser.analyse({"dev": {"A": "1", "B": "2"}})
        assert report.unique_count == 2
        assert report.shared_count == 0

    def test_repr_contains_counts(self, analyser, sample_profiles):
        report = analyser.analyse(sample_profiles)
        r = repr(report)
        assert "unique=" in r
        assert "shared=" in r
