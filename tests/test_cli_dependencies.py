"""Tests for envchain.cli_dependencies."""
import sys
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from envchain.cli_dependencies import DependencyCommand
from envchain.models import Profile


def _make_profile(name: str, variables: dict) -> Profile:
    p = Profile(name=name)
    p.variables = variables
    return p


@pytest.fixture
def mock_storage():
    storage = MagicMock()
    storage.list_profiles.return_value = ["base", "app"]
    base = _make_profile("base", {"DB_HOST": "localhost"})
    app = _make_profile(
        "app", {"URL": "http://${base:DB_HOST}/path", "PLAIN": "value"}
    )
    storage.load_profile.side_effect = lambda name, password: (
        base if name == "base" else app
    )
    return storage


@pytest.fixture
def cmd(mock_storage):
    return DependencyCommand(mock_storage)


class TestDependencyCommand:
    def test_run_prints_edges(self, cmd, capsys):
        cmd.run("app")
        captured = capsys.readouterr()
        assert "base" in captured.out

    def test_run_unknown_profile_exits(self, cmd):
        with pytest.raises(SystemExit) as exc:
            cmd.run("nonexistent")
        assert exc.value.code == 1

    def test_run_no_edges_prints_message(self, cmd, capsys):
        cmd.run("base")
        captured = capsys.readouterr()
        assert "No cross-profile" in captured.out

    def test_run_show_missing_only_no_missing(self, cmd, capsys):
        cmd.run("app", show_missing_only=True)
        captured = capsys.readouterr()
        assert "No missing" in captured.out

    def test_run_show_missing_only_with_missing(self, mock_storage, capsys):
        broken = _make_profile("app", {"X": "${ghost:NOPE}"})
        mock_storage.load_profile.side_effect = lambda name, password: (
            _make_profile("base", {}) if name == "base" else broken
        )
        cmd = DependencyCommand(mock_storage)
        with pytest.raises(SystemExit):
            cmd.run("app", show_missing_only=False)

    def test_show_graph_no_edges_prints_message(self, cmd, capsys):
        cmd.show_graph("base")
        captured = capsys.readouterr()
        assert "no outgoing" in captured.out

    def test_show_graph_prints_arrow(self, cmd, capsys):
        cmd.show_graph("app")
        captured = capsys.readouterr()
        assert "-->" in captured.out
