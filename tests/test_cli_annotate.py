"""Tests for cli_annotate module."""
import pytest
import sys
from envchain.cli_annotate import AnnotateCommand


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def cmd(tmp_dir):
    return AnnotateCommand(tmp_dir, "dev")


class TestAnnotateCommand:
    def test_add_prints_confirmation(self, cmd, capsys):
        cmd.add("DB_URL", "Primary database URL")
        out = capsys.readouterr().out
        assert "DB_URL" in out
        assert "dev" in out

    def test_add_with_author_in_output(self, cmd, capsys):
        cmd.add("TOKEN", "Auth token", author="alice")
        out = capsys.readouterr().out
        assert "TOKEN" in out

    def test_add_empty_var_name_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.add("", "some note")

    def test_add_empty_note_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.add("KEY", "")

    def test_remove_existing_prints_confirmation(self, cmd, capsys):
        cmd.add("KEY", "note")
        capsys.readouterr()
        cmd.remove("KEY")
        out = capsys.readouterr().out
        assert "KEY" in out

    def test_remove_missing_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.remove("NONEXISTENT")

    def test_show_existing(self, cmd, capsys):
        cmd.add("DB_HOST", "Database host", author="bob")
        capsys.readouterr()
        cmd.show("DB_HOST")
        out = capsys.readouterr().out
        assert "DB_HOST" in out
        assert "Database host" in out
        assert "bob" in out

    def test_show_missing_prints_no_annotation(self, cmd, capsys):
        cmd.show("MISSING")
        out = capsys.readouterr().out
        assert "No annotation" in out

    def test_list_all_empty_prints_message(self, cmd, capsys):
        cmd.list_all()
        out = capsys.readouterr().out
        assert "No annotations" in out

    def test_list_all_shows_entries(self, cmd, capsys):
        cmd.add("A", "note a")
        cmd.add("B", "note b")
        capsys.readouterr()
        cmd.list_all()
        out = capsys.readouterr().out
        assert "A" in out
        assert "B" in out
