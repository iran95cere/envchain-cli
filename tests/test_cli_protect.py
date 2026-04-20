"""Tests for envchain.cli_protect."""
import pytest
from envchain.cli_protect import ProtectCommand
from envchain.env_protect import ProtectManager


@pytest.fixture()
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture()
def cmd(tmp_dir):
    return ProtectCommand(tmp_dir)


class TestProtectCommand:
    def test_add_prints_confirmation(self, cmd, capsys):
        cmd.add("dev", "SECRET")
        out = capsys.readouterr().out
        assert "SECRET" in out
        assert "dev" in out

    def test_add_with_reason_in_output(self, cmd, capsys):
        cmd.add("dev", "TOKEN", reason="do not overwrite")
        out = capsys.readouterr().out
        assert "do not overwrite" in out

    def test_remove_existing_prints_confirmation(self, cmd, capsys):
        cmd.add("dev", "KEY")
        capsys.readouterr()
        cmd.remove("dev", "KEY")
        out = capsys.readouterr().out
        assert "Removed" in out

    def test_remove_nonexistent_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.remove("dev", "GHOST")

    def test_status_protected(self, cmd, capsys):
        cmd.add("dev", "X")
        capsys.readouterr()
        cmd.status("dev", "X")
        out = capsys.readouterr().out
        assert "PROTECTED" in out

    def test_status_not_protected(self, cmd, capsys):
        cmd.status("dev", "MISSING")
        out = capsys.readouterr().out
        assert "not protected" in out

    def test_list_protected_prints_names(self, cmd, capsys):
        cmd.add("dev", "A")
        cmd.add("dev", "B")
        capsys.readouterr()
        cmd.list_protected("dev")
        out = capsys.readouterr().out
        assert "A" in out
        assert "B" in out

    def test_list_protected_empty_profile(self, cmd, capsys):
        cmd.list_protected("empty")
        out = capsys.readouterr().out
        assert "No protected" in out
