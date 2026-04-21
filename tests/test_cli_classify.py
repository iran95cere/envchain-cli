"""Tests for envchain.cli_classify."""
from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from envchain.cli_classify import ClassifyCommand
from envchain.models import Profile


@pytest.fixture
def mock_storage():
    storage = MagicMock()
    profile = Profile(name="dev", vars={
        "DB_PASSWORD": "secret",
        "APP_HOST": "localhost",
        "DEBUG": "true",
        "GREETING": "hello",
    })
    storage.load_profile.return_value = profile
    return storage


@pytest.fixture
def cmd(mock_storage):
    return ClassifyCommand(storage=mock_storage)


class TestClassifyCommand:
    def test_run_prints_categories(self, cmd, capsys):
        cmd.run("dev", "pass")
        out = capsys.readouterr().out
        assert "secret" in out
        assert "network" in out or "debug" in out

    def test_run_with_category_filter(self, cmd, capsys):
        cmd.run("dev", "pass", category_filter="secret")
        out = capsys.readouterr().out
        assert "DB_PASSWORD" in out

    def test_run_filter_no_match_prints_message(self, cmd, capsys):
        cmd.run("dev", "pass", category_filter="database")
        out = capsys.readouterr().out
        assert "No variables found" in out

    def test_run_missing_profile_exits(self, mock_storage, capsys):
        mock_storage.load_profile.return_value = None
        cmd = ClassifyCommand(storage=mock_storage)
        with pytest.raises(SystemExit):
            cmd.run("missing", "pass")

    def test_list_categories_prints_known_categories(self, cmd, capsys):
        cmd.list_categories()
        out = capsys.readouterr().out
        assert "secret" in out
        assert "database" in out
        assert "general" in out
