"""Tests for envchain.env_watch."""
from __future__ import annotations

import os
import tempfile
import time

import pytest

from envchain.env_watch import ProfileWatcher, WatchEvent


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def watcher(tmp_dir):
    return ProfileWatcher(tmp_dir, poll_interval=0.05)


# ---------------------------------------------------------------------------
class TestWatchEvent:
    def test_to_dict_contains_required_keys(self):
        ev = WatchEvent("prod", "created", detected_at=1000.0)
        d = ev.to_dict()
        assert d["profile_name"] == "prod"
        assert d["event_type"] == "created"
        assert d["detected_at"] == 1000.0

    def test_repr_contains_profile_and_type(self):
        ev = WatchEvent("dev", "modified")
        r = repr(ev)
        assert "dev" in r
        assert "modified" in r


# ---------------------------------------------------------------------------
class TestProfileWatcher:
    def test_poll_detects_created_file(self, tmp_dir, watcher):
        watcher.poll()  # baseline
        path = os.path.join(tmp_dir, "staging.enc")
        open(path, "w").close()
        events = watcher.poll()
        types = [e.event_type for e in events]
        assert "created" in types
        assert any(e.profile_name == "staging" for e in events)

    def test_poll_detects_deleted_file(self, tmp_dir, watcher):
        path = os.path.join(tmp_dir, "old.enc")
        open(path, "w").close()
        watcher.poll()  # baseline
        os.remove(path)
        events = watcher.poll()
        assert any(e.event_type == "deleted" and e.profile_name == "old" for e in events)

    def test_poll_detects_modified_file(self, tmp_dir, watcher):
        path = os.path.join(tmp_dir, "dev.enc")
        open(path, "w").close()
        watcher.poll()  # baseline
        time.sleep(0.05)
        with open(path, "w") as f:
            f.write("changed")
        os.utime(path, (time.time() + 1, time.time() + 1))
        events = watcher.poll()
        assert any(e.event_type == "modified" and e.profile_name == "dev" for e in events)

    def test_handler_is_called_on_event(self, tmp_dir, watcher):
        received = []
        watcher.on_change(received.append)
        watcher.poll()
        open(os.path.join(tmp_dir, "ci.enc"), "w").close()
        watcher.poll()
        assert len(received) == 1
        assert received[0].profile_name == "ci"

    def test_empty_dir_returns_no_events(self, tmp_dir, watcher):
        watcher.poll()
        events = watcher.poll()
        assert events == []

    def test_non_enc_files_ignored(self, tmp_dir, watcher):
        watcher.poll()
        open(os.path.join(tmp_dir, "notes.txt"), "w").close()
        events = watcher.poll()
        assert events == []

    def test_run_limited_cycles(self, tmp_dir):
        w = ProfileWatcher(tmp_dir, poll_interval=0.01)
        w.run(max_cycles=3)  # should return without hanging
