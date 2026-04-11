"""Tests for envchain.env_stats."""
import pytest
from envchain.env_stats import EnvStats, ProfileStats


@pytest.fixture
def stats():
    return EnvStats()


class TestProfileStats:
    def test_to_dict_contains_required_keys(self):
        ps = ProfileStats(profile_name="dev", var_count=3)
        d = ps.to_dict()
        assert "profile_name" in d
        assert "var_count" in d
        assert "empty_value_count" in d
        assert "longest_key" in d
        assert "shortest_key" in d
        assert "avg_value_length" in d
        assert "key_prefixes" in d

    def test_repr_contains_profile_name(self):
        ps = ProfileStats(profile_name="staging", var_count=5)
        assert "staging" in repr(ps)
        assert "5" in repr(ps)


class TestEnvStats:
    def test_empty_variables_returns_zeroed_stats(self, stats):
        result = stats.compute("empty", {})
        assert result.var_count == 0
        assert result.empty_value_count == 0
        assert result.longest_key is None
        assert result.shortest_key is None
        assert result.avg_value_length == 0.0

    def test_var_count(self, stats):
        variables = {"A": "1", "BB": "2", "CCC": "3"}
        result = stats.compute("dev", variables)
        assert result.var_count == 3

    def test_empty_value_count(self, stats):
        variables = {"A": "", "B": "value", "C": ""}
        result = stats.compute("dev", variables)
        assert result.empty_value_count == 2

    def test_longest_and_shortest_key(self, stats):
        variables = {"A": "x", "LONGKEY": "y", "MED": "z"}
        result = stats.compute("dev", variables)
        assert result.longest_key == "LONGKEY"
        assert result.shortest_key == "A"

    def test_avg_value_length(self, stats):
        variables = {"A": "12", "B": "1234"}
        result = stats.compute("dev", variables)
        assert result.avg_value_length == 3.0

    def test_key_prefixes_grouped_by_underscore(self, stats):
        variables = {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "APP_NAME": "myapp",
        }
        result = stats.compute("dev", variables)
        assert result.key_prefixes["DB"] == 2
        assert result.key_prefixes["APP"] == 1

    def test_key_without_underscore_uses_full_key_as_prefix(self, stats):
        variables = {"MYVAR": "value"}
        result = stats.compute("dev", variables)
        assert result.key_prefixes["MYVAR"] == 1

    def test_summarise_many_returns_sorted_by_name(self, stats):
        profiles = {
            "prod": {"X": "1"},
            "dev": {"Y": "2"},
            "staging": {"Z": "3"},
        }
        results = stats.summarise_many(profiles)
        names = [r.profile_name for r in results]
        assert names == ["dev", "prod", "staging"]

    def test_summarise_many_empty_input(self, stats):
        assert stats.summarise_many({}) == []
