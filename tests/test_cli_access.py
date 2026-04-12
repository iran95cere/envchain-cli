"""Tests for envchain.cli_access."""
import pytest
from envchain.cli_access import AccessCommand
from envchain.env_access import AccessManager, AccessRule


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def cmd(tmp_dir):
    return AccessCommand(tmp_dir)


class TestAccessCommand:
    def test_add_prints_confirmation(self, cmd, capsys):
        cmd.add("prod", allowed=["alice"], denied=[], read_only=False)
        out = capsys.readouterr().out
        assert "prod" in out
        assert "Access rule set" in out

    def test_add_read_only_mentions_mode(self, cmd, capsys):
        cmd.add("prod", allowed=[], denied=[], read_only=True)
        out = capsys.readouterr().out
        assert "read-only" in out

    def test_add_denied_users_listed(self, cmd, capsys):
        cmd.add("prod", allowed=[], denied=["mallory"], read_only=False)
        out = capsys.readouterr().out
        assert "mallory" in out

    def test_remove_existing_rule(self, cmd, capsys):
        cmd.add("dev", allowed=[], denied=[], read_only=False)
        capsys.readouterr()
        cmd.remove("dev")
        out = capsys.readouterr().out
        assert "removed" in out

    def test_remove_nonexistent_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.remove("ghost")

    def test_check_allowed_prints_allowed(self, cmd, capsys):
        cmd.add("dev", allowed=["alice"], denied=[], read_only=False)
        capsys.readouterr()
        cmd.check("dev", "alice")
        out = capsys.readouterr().out
        assert "ALLOWED" in out

    def test_check_denied_exits(self, cmd):
        cmd.add("prod", allowed=[], denied=["eve"], read_only=False)
        with pytest.raises(SystemExit):
            cmd.check("prod", "eve")

    def test_list_rules_empty_message(self, cmd, capsys):
        cmd.list_rules()
        out = capsys.readouterr().out
        assert "No access rules" in out

    def test_list_rules_shows_profiles(self, cmd, capsys):
        cmd.add("alpha", allowed=["alice"], denied=[], read_only=False)
        cmd.add("beta", allowed=[], denied=["bob"], read_only=True)
        capsys.readouterr()
        cmd.list_rules()
        out = capsys.readouterr().out
        assert "alpha" in out
        assert "beta" in out
        assert "read-only" in out
