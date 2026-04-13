"""Tests for envchain.env_version."""
from __future__ import annotations

import os
import time

import pytest

from envchain.env_version import VersionEntry, VersionManager


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def manager(tmp_dir):
    return VersionManager(tmp_dir, "dev")


SAMPLE_VARS = {"API_KEY": "abc123", "DEBUG": "true"}


class TestVersionEntry:
    def test_to_dict_contains_required_keys(self):
        e = VersionEntry(profile="dev", version=1, timestamp=1000.0, message="init")
        d = e.to_dict()
        assert "profile" in d
        assert "version" in d
        assert "timestamp" in d
        assert "message" in d
        assert "snapshot" in d

    def test_from_dict_roundtrip(self):
        e = VersionEntry(
            profile="prod", version=3, timestamp=9999.0,
            author="alice", message="bump", snapshot={"X": "1"}
        )
        assert VersionEntry.from_dict(e.to_dict()).version == 3
        assert VersionEntry.from_dict(e.to_dict()).author == "alice"
        assert VersionEntry.from_dict(e.to_dict()).snapshot == {"X": "1"}

    def test_from_dict_missing_optional_fields_default(self):
        e = VersionEntry.from_dict({"profile": "x", "version": 1, "timestamp": 0.0})
        assert e.author == ""
        assert e.message == ""
        assert e.snapshot == {}

    def test_repr_contains_profile_and_version(self):
        e = VersionEntry(profile="dev", version=2, timestamp=0.0, message="hello")
        r = repr(e)
        assert "dev" in r
        assert "2" in r


class TestVersionManager:
    def test_history_empty_initially(self, manager):
        assert manager.history() == []

    def test_commit_increments_version(self, manager):
        e1 = manager.commit(SAMPLE_VARS, message="first")
        e2 = manager.commit(SAMPLE_VARS, message="second")
        assert e1.version == 1
        assert e2.version == 2

    def test_commit_stores_snapshot(self, manager):
        entry = manager.commit(SAMPLE_VARS)
        assert entry.snapshot == SAMPLE_VARS

    def test_get_returns_correct_entry(self, manager):
        manager.commit(SAMPLE_VARS, message="v1")
        manager.commit({"X": "y"}, message="v2")
        e = manager.get(2)
        assert e is not None
        assert e.message == "v2"

    def test_get_returns_none_for_missing(self, manager):
        assert manager.get(99) is None

    def test_latest_returns_last_entry(self, manager):
        manager.commit(SAMPLE_VARS, message="a")
        manager.commit(SAMPLE_VARS, message="b")
        assert manager.latest().message == "b"

    def test_latest_returns_none_when_empty(self, manager):
        assert manager.latest() is None

    def test_clear_removes_all_entries(self, manager):
        manager.commit(SAMPLE_VARS)
        manager.clear()
        assert manager.history() == []

    def test_persistence_across_instances(self, tmp_dir):
        m1 = VersionManager(tmp_dir, "staging")
        m1.commit({"FOO": "bar"}, message="persist")
        m2 = VersionManager(tmp_dir, "staging")
        assert len(m2.history()) == 1
        assert m2.latest().message == "persist"
