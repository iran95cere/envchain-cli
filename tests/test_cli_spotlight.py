"""Tests for SpotlightCommand CLI wrapper."""
import io
import sys
from unittest.mock import MagicMock

import pytest

from envchain.cli_spotlight import SpotlightCommand
from envchain.models import Profile


def _make_profile(vars_: dict) -> Profile:
    p = Profile(name="dev", vars=vars_)
    return p


@pytest.fixture
def mock_storage():
    storage = MagicMock()
    storage.load_profile.return_value = _make_profile(
        {
            "API_TOKEN": "secret",
            "DEBUG": "false",
            "APP_NAME": "myapp",
        }
    )
    return storage


@pytest.fixture
def cmd(mock_storage):
    return SpotlightCommand(storage=mock_storage)


class TestSpotlightCommand:
    def test_run_prints_header(self, cmd):
        buf = io.StringIO()
        cmd.run("dev", "pass", out=buf)
        assert "Spotlight" in buf.getvalue()

    def test_run_includes_high_priority_var(self, cmd):
        buf = io.StringIO()
        cmd.run("dev", "pass", top=10, out=buf)
        assert "API_TOKEN" in buf.getvalue()

    def test_run_min_score_filters_low_priority(self, cmd):
        buf = io.StringIO()
        cmd.run("dev", "pass", top=10, min_score=8, out=buf)
        output = buf.getvalue()
        assert "DEBUG" not in output

    def test_run_missing_profile_exits(self, mock_storage):
        mock_storage.load_profile.return_value = None
        cmd = SpotlightCommand(storage=mock_storage)
        with pytest.raises(SystemExit):
            cmd.run("missing", "pass")

    def test_show_all_prints_all_vars(self, cmd):
        buf = io.StringIO()
        cmd.show_all("dev", "pass", out=buf)
        output = buf.getvalue()
        assert "API_TOKEN" in output
        assert "DEBUG" in output

    def test_run_empty_profile_prints_message(self, mock_storage):
        mock_storage.load_profile.return_value = _make_profile({})
        cmd = SpotlightCommand(storage=mock_storage)
        buf = io.StringIO()
        cmd.run("dev", "pass", out=buf)
        assert "No variables" in buf.getvalue()
