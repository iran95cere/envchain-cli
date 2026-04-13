"""Tests for envchain.cli_preset."""
import pytest

from envchain.env_preset import PresetManager
from envchain.cli_preset import PresetCommand


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def manager(tmp_dir):
    return PresetManager(tmp_dir)


@pytest.fixture
def cmd(manager):
    return PresetCommand(manager)


class TestPresetCommand:
    def test_add_valid_prints_ok(self, cmd, capsys):
        cmd.add("dev", "Dev preset", ["DEBUG=true", "LOG=verbose"])
        out = capsys.readouterr().out
        assert "dev" in out
        assert "2" in out

    def test_add_invalid_assignment_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.add("bad", "", ["NODEQUALS"])

    def test_add_empty_name_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.add("", "", ["K=V"])

    def test_remove_existing_prints_ok(self, cmd, manager, capsys):
        manager.add("to_remove", "", {"A": "1"})
        cmd.remove("to_remove")
        out = capsys.readouterr().out
        assert "removed" in out

    def test_remove_nonexistent_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.remove("ghost")

    def test_list_presets_empty_message(self, cmd, capsys):
        cmd.list_presets()
        out = capsys.readouterr().out
        assert "No presets" in out

    def test_list_presets_shows_names(self, cmd, manager, capsys):
        manager.add("alpha", "First", {"X": "1"})
        manager.add("beta", "", {})
        cmd.list_presets()
        out = capsys.readouterr().out
        assert "alpha" in out
        assert "beta" in out

    def test_show_existing_preset(self, cmd, manager, capsys):
        manager.add("show_me", "A description", {"FOO": "bar"})
        cmd.show("show_me")
        out = capsys.readouterr().out
        assert "show_me" in out
        assert "FOO" in out
        assert "bar" in out

    def test_show_nonexistent_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.show("missing")
