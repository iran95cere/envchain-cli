"""Tests for envchain.cli_changelog."""
import pytest
from envchain.cli_changelog import ChangelogCommand


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def cmd(tmp_dir):
    return ChangelogCommand(tmp_dir)


@pytest.fixture
def populated_cmd(tmp_dir):
    c = ChangelogCommand(tmp_dir)
    c._manager.record("dev", "FOO", "set", new_value="bar")
    c._manager.record("dev", "BAZ", "delete", old_value="old")
    c._manager.record("prod", "QUX", "rename", old_value="QUX", new_value="QUUX")
    return c


class TestChangelogCommand:
    def test_show_empty_prints_message(self, cmd, capsys):
        cmd.show()
        out = capsys.readouterr().out
        assert "No changelog entries found" in out

    def test_show_all_entries(self, populated_cmd, capsys):
        populated_cmd.show()
        out = capsys.readouterr().out
        assert "FOO" in out
        assert "BAZ" in out
        assert "QUX" in out

    def test_show_filtered_by_profile(self, populated_cmd, capsys):
        populated_cmd.show(profile="prod")
        out = capsys.readouterr().out
        assert "QUX" in out
        assert "FOO" not in out

    def test_clear_all_prints_count(self, populated_cmd, capsys):
        populated_cmd.clear()
        out = capsys.readouterr().out
        assert "3" in out

    def test_clear_by_profile(self, populated_cmd, capsys):
        populated_cmd.clear(profile="dev")
        out = capsys.readouterr().out
        assert "2" in out
        assert "dev" in out

    def test_last_prints_entries(self, populated_cmd, capsys):
        populated_cmd.last(n=2)
        out = capsys.readouterr().out
        # Should print at most 2 entries
        lines = [l for l in out.strip().splitlines() if l]
        assert len(lines) <= 2

    def test_last_empty_prints_no_entries(self, cmd, capsys):
        cmd.last()
        out = capsys.readouterr().out
        assert "No entries" in out
