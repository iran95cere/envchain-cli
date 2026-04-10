"""Tests for envchain.alias and envchain.cli_alias."""
from __future__ import annotations

import pytest

from envchain.alias import AliasManager
from envchain.cli_alias import AliasCommand


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_dir(tmp_path):
    return tmp_path


@pytest.fixture()
def manager(tmp_dir):
    return AliasManager(tmp_dir)


@pytest.fixture()
def cmd(tmp_dir):
    return AliasCommand(str(tmp_dir))


# ---------------------------------------------------------------------------
# AliasManager unit tests
# ---------------------------------------------------------------------------

class TestAliasManager:
    def test_add_and_resolve(self, manager):
        manager.add("prod", "production")
        assert manager.resolve("prod") == "production"

    def test_resolve_missing_returns_none(self, manager):
        assert manager.resolve("nope") is None

    def test_add_empty_alias_raises(self, manager):
        with pytest.raises(ValueError, match="empty"):
            manager.add("", "production")

    def test_add_empty_profile_raises(self, manager):
        with pytest.raises(ValueError, match="empty"):
            manager.add("prod", "")

    def test_alias_equals_profile_raises(self, manager):
        with pytest.raises(ValueError, match="differ"):
            manager.add("staging", "staging")

    def test_remove_existing(self, manager):
        manager.add("dev", "development")
        assert manager.remove("dev") is True
        assert manager.resolve("dev") is None

    def test_remove_missing_returns_false(self, manager):
        assert manager.remove("ghost") is False

    def test_list_aliases_sorted(self, manager):
        manager.add("z", "zulu")
        manager.add("a", "alpha")
        entries = manager.list_aliases()
        assert [e["alias"] for e in entries] == ["a", "z"]

    def test_aliases_for_profile(self, manager):
        manager.add("p", "prod")
        manager.add("production", "prod")
        result = sorted(manager.aliases_for_profile("prod"))
        assert result == ["p", "production"]

    def test_rename_profile_updates_aliases(self, manager):
        manager.add("p", "old-name")
        manager.add("q", "old-name")
        count = manager.rename_profile("old-name", "new-name")
        assert count == 2
        assert manager.resolve("p") == "new-name"
        assert manager.resolve("q") == "new-name"

    def test_persistence_across_instances(self, tmp_dir):
        m1 = AliasManager(tmp_dir)
        m1.add("dev", "development")
        m2 = AliasManager(tmp_dir)
        assert m2.resolve("dev") == "development"


# ---------------------------------------------------------------------------
# AliasCommand (CLI) tests
# ---------------------------------------------------------------------------

class TestAliasCommand:
    def test_add_prints_confirmation(self, cmd, capsys):
        cmd.add("dev", "development")
        out = capsys.readouterr().out
        assert "dev" in out and "development" in out

    def test_add_invalid_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.add("", "development")

    def test_remove_success(self, cmd, capsys):
        cmd.add("dev", "development")
        cmd.remove("dev")
        out = capsys.readouterr().out
        assert "removed" in out

    def test_remove_missing_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.remove("ghost")

    def test_list_empty(self, cmd, capsys):
        cmd.list_aliases()
        assert "No aliases" in capsys.readouterr().out

    def test_resolve_found(self, cmd, capsys):
        cmd.add("p", "production")
        cmd.resolve("p")
        assert "production" in capsys.readouterr().out

    def test_resolve_missing_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.resolve("missing")
