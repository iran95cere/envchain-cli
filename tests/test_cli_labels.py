"""Tests for envchain.cli_labels."""
import json
import sys
import pytest
from pathlib import Path
from envchain.cli_labels import LabelsCommand


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def cmd(tmp_dir):
    return LabelsCommand(tmp_dir)


class TestLabelsCommand:
    def test_add_creates_file(self, cmd, tmp_dir):
        cmd.add("DB_URL", "database")
        labels_file = Path(tmp_dir) / "labels.json"
        assert labels_file.exists()

    def test_add_prints_confirmation(self, cmd, capsys):
        cmd.add("API_KEY", "secret")
        out = capsys.readouterr().out
        assert "API_KEY" in out
        assert "secret" in out

    def test_add_empty_var_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.add("", "label")

    def test_remove_existing_prints_confirmation(self, cmd, capsys):
        cmd.add("PORT", "network")
        capsys.readouterr()
        cmd.remove("PORT")
        out = capsys.readouterr().out
        assert "PORT" in out

    def test_remove_missing_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.remove("NONEXISTENT")

    def test_list_labels_empty(self, cmd, capsys):
        cmd.list_labels()
        out = capsys.readouterr().out
        assert "No labels" in out

    def test_list_labels_shows_entries(self, cmd, capsys):
        cmd.add("DB_HOST", "database", "Primary host")
        capsys.readouterr()
        cmd.list_labels()
        out = capsys.readouterr().out
        assert "DB_HOST" in out
        assert "database" in out
        assert "Primary host" in out

    def test_find_prints_matches(self, cmd, capsys):
        cmd.add("DB_HOST", "database")
        cmd.add("DB_PORT", "database")
        cmd.add("API_KEY", "secret")
        capsys.readouterr()
        cmd.find("database")
        out = capsys.readouterr().out
        assert "DB_HOST" in out
        assert "DB_PORT" in out
        assert "API_KEY" not in out

    def test_find_no_matches_prints_message(self, cmd, capsys):
        cmd.find("nonexistent")
        out = capsys.readouterr().out
        assert "No variables" in out
