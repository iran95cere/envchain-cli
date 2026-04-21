"""Tests for env_pin_profile and cli_pin_profile."""
from __future__ import annotations

import os
import pytest

from envchain.env_pin_profile import PinProfileEntry, PinProfileManager
from envchain.cli_pin_profile import PinProfileCommand


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def manager(tmp_dir):
    return PinProfileManager(tmp_dir)


@pytest.fixture
def cmd(tmp_dir):
    return PinProfileCommand(tmp_dir)


class TestPinProfileEntry:
    def test_to_dict_contains_required_keys(self):
        entry = PinProfileEntry(profile="dev", directory="/tmp", created_at="2024-01-01")
        d = entry.to_dict()
        assert "profile" in d
        assert "directory" in d
        assert "created_at" in d

    def test_from_dict_roundtrip(self):
        original = PinProfileEntry(profile="prod", directory="/home/user", created_at="2024-06-01")
        restored = PinProfileEntry.from_dict(original.to_dict())
        assert restored.profile == original.profile
        assert restored.directory == original.directory
        assert restored.created_at == original.created_at

    def test_from_dict_missing_created_at_defaults_empty(self):
        entry = PinProfileEntry.from_dict({"profile": "dev", "directory": "/tmp"})
        assert entry.created_at == ""

    def test_repr_contains_profile_and_directory(self):
        entry = PinProfileEntry(profile="staging", directory="/code", created_at="")
        r = repr(entry)
        assert "staging" in r
        assert "/code" in r


class TestPinProfileManager:
    def test_list_pins_empty_initially(self, manager):
        assert manager.list_pins() == []

    def test_pin_creates_entry(self, manager, tmp_dir):
        entry = manager.pin(tmp_dir, "dev")
        assert entry.profile == "dev"
        pins = manager.list_pins()
        assert len(pins) == 1

    def test_resolve_returns_profile(self, manager, tmp_dir):
        manager.pin(tmp_dir, "prod")
        result = manager.resolve(tmp_dir)
        assert result == "prod"

    def test_resolve_returns_none_for_unknown(self, manager, tmp_dir):
        result = manager.resolve(tmp_dir)
        assert result is None

    def test_unpin_removes_entry(self, manager, tmp_dir):
        manager.pin(tmp_dir, "dev")
        removed = manager.unpin(tmp_dir)
        assert removed is True
        assert manager.list_pins() == []

    def test_unpin_returns_false_when_not_found(self, manager, tmp_dir):
        assert manager.unpin(tmp_dir) is False

    def test_persists_across_instances(self, tmp_dir):
        m1 = PinProfileManager(tmp_dir)
        m1.pin(tmp_dir, "ci")
        m2 = PinProfileManager(tmp_dir)
        assert m2.resolve(tmp_dir) == "ci"


class TestPinProfileCommand:
    def test_pin_prints_confirmation(self, cmd, tmp_dir, capsys):
        cmd.pin(tmp_dir, "dev")
        out = capsys.readouterr().out
        assert "dev" in out
        assert "Pinned" in out

    def test_resolve_prints_profile(self, cmd, tmp_dir, capsys):
        cmd.pin(tmp_dir, "staging")
        cmd.resolve(tmp_dir)
        out = capsys.readouterr().out
        assert "staging" in out

    def test_resolve_exits_when_not_found(self, cmd, tmp_dir):
        with pytest.raises(SystemExit):
            cmd.resolve(tmp_dir)

    def test_unpin_exits_when_not_found(self, cmd, tmp_dir):
        with pytest.raises(SystemExit):
            cmd.unpin(tmp_dir)

    def test_list_pins_empty_message(self, cmd, capsys):
        cmd.list_pins()
        out = capsys.readouterr().out
        assert "No directory pins" in out
