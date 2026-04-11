"""Tests for envchain.cli_watch."""
from __future__ import annotations

import io
import os
import time

import pytest

from envchain.cli_watch import WatchCommand


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def cmd(tmp_dir):
    return WatchCommand(tmp_dir, poll_interval=0.01)


class TestWatchCommand:
    def test_run_max_cycles_no_crash(self, cmd):
        out = io.StringIO()
        cmd.run(max_cycles=2, out=out)

    def test_run_prints_created_event(self, tmp_dir):
        cmd = WatchCommand(tmp_dir, poll_interval=0.01)
        out = io.StringIO()

        # We drive a single poll cycle manually via max_cycles=1 after file creation
        open(os.path.join(tmp_dir, "prod.enc"), "w").close()
        cmd.run(max_cycles=1, out=out)
        value = out.getvalue()
        assert "prod" in value
        assert "created" in value

    def test_run_profile_filter_excludes_others(self, tmp_dir):
        cmd = WatchCommand(tmp_dir, poll_interval=0.01)
        out = io.StringIO()
        open(os.path.join(tmp_dir, "prod.enc"), "w").close()
        open(os.path.join(tmp_dir, "dev.enc"), "w").close()
        cmd.run(profile_filter="prod", max_cycles=1, out=out)
        value = out.getvalue()
        assert "prod" in value
        assert "dev" not in value

    def test_show_status_no_profiles(self, tmp_dir):
        cmd = WatchCommand(tmp_dir)
        out = io.StringIO()
        cmd.show_status(out=out)
        assert "No profiles" in out.getvalue()

    def test_show_status_lists_profiles(self, tmp_dir):
        open(os.path.join(tmp_dir, "staging.enc"), "w").close()
        cmd = WatchCommand(tmp_dir)
        out = io.StringIO()
        cmd.show_status(out=out)
        assert "staging" in out.getvalue()
