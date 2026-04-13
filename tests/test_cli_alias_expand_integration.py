"""Integration-style tests for alias expansion with a real in-memory profile."""
import pytest
from unittest.mock import MagicMock

from envchain.env_alias_expand import EnvAliasExpander
from envchain.models import Profile


def _make_profile(name: str, **vars_: str) -> Profile:
    return Profile(name=name, variables=dict(vars_))


class TestAliasExpandIntegration:
    def test_full_expand_roundtrip(self):
        expander = EnvAliasExpander()
        profile = _make_profile(
            "prod",
            DB_HOST="db.prod.example.com",
            DB_PORT="5432",
            API_KEY="super-secret",
        )
        alias_map = {
            "DATABASE_HOST": "DB_HOST",
            "DATABASE_PORT": "DB_PORT",
            "SERVICE_API_KEY": "API_KEY",
        }
        report = expander.expand(profile.variables, alias_map)

        assert report.expanded_count == 3
        assert profile.variables["DATABASE_HOST"] == "db.prod.example.com"
        assert profile.variables["DATABASE_PORT"] == "5432"
        assert profile.variables["SERVICE_API_KEY"] == "super-secret"
        # originals untouched
        assert profile.variables["DB_HOST"] == "db.prod.example.com"

    def test_overwrite_false_preserves_existing_alias(self):
        expander = EnvAliasExpander()
        profile = _make_profile(
            "staging",
            DB_HOST="staging-db",
            DATABASE_HOST="do-not-touch",
        )
        report = expander.expand(
            profile.variables, {"DATABASE_HOST": "DB_HOST"}, overwrite=False
        )
        assert report.expanded_count == 0
        assert profile.variables["DATABASE_HOST"] == "do-not-touch"

    def test_overwrite_true_replaces_existing_alias(self):
        expander = EnvAliasExpander()
        profile = _make_profile(
            "staging",
            DB_HOST="staging-db",
            DATABASE_HOST="do-not-touch",
        )
        report = expander.expand(
            profile.variables, {"DATABASE_HOST": "DB_HOST"}, overwrite=True
        )
        assert report.expanded_count == 1
        assert profile.variables["DATABASE_HOST"] == "staging-db"

    def test_partial_alias_map_some_missing(self):
        expander = EnvAliasExpander()
        profile = _make_profile("dev", DB_HOST="localhost")
        alias_map = {
            "DATABASE_HOST": "DB_HOST",   # present
            "CACHE_HOST": "REDIS_HOST",   # missing
        }
        report = expander.expand(profile.variables, alias_map)
        assert report.expanded_count == 1
        assert report.skipped_count == 1
        assert "DATABASE_HOST" in profile.variables
        assert "CACHE_HOST" not in profile.variables
