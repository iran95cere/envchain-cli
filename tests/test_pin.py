"""Tests for envchain.pin.PinManager."""
import time
import pytest
from unittest.mock import patch
from envchain.pin import PinManager, PinError


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def manager(tmp_dir):
    return PinManager(tmp_dir)


class TestPinManager:
    def test_has_pin_false_when_not_set(self, manager):
        assert manager.has_pin("dev") is False

    def test_set_pin_marks_has_pin(self, manager):
        manager.set_pin("dev", "1234")
        assert manager.has_pin("dev") is True

    def test_verify_pin_correct(self, manager):
        manager.set_pin("dev", "1234")
        manager.verify_pin("dev", "1234")  # should not raise

    def test_verify_pin_incorrect_raises(self, manager):
        manager.set_pin("dev", "1234")
        with pytest.raises(PinError, match="Incorrect PIN"):
            manager.verify_pin("dev", "0000")

    def test_verify_pin_no_pin_set_passes(self, manager):
        manager.verify_pin("dev", "anything")  # should not raise

    def test_set_pin_too_short_raises(self, manager):
        with pytest.raises(PinError, match="at least 4 digits"):
            manager.set_pin("dev", "12")

    def test_set_pin_non_numeric_raises(self, manager):
        with pytest.raises(PinError, match="at least 4 digits"):
            manager.set_pin("dev", "abcd")

    def test_remove_pin_returns_true_when_existed(self, manager):
        manager.set_pin("dev", "1234")
        assert manager.remove_pin("dev") is True
        assert manager.has_pin("dev") is False

    def test_remove_pin_returns_false_when_missing(self, manager):
        assert manager.remove_pin("ghost") is False

    def test_failed_attempts_counted(self, manager):
        manager.set_pin("dev", "1234")
        for _ in range(3):
            with pytest.raises(PinError):
                manager.verify_pin("dev", "wrong")
        rec = manager._data["dev"]
        assert rec["attempts"] == 3

    def test_lockout_after_max_attempts(self, manager):
        manager.set_pin("dev", "1234")
        for _ in range(4):  # 4 failures before final
            try:
                manager.verify_pin("dev", "bad")
            except PinError:
                pass
        with pytest.raises(PinError, match="locked"):
            manager.verify_pin("dev", "bad")

    def test_locked_profile_rejects_correct_pin(self, manager):
        manager.set_pin("dev", "1234")
        # force locked state
        manager._data["dev"]["locked_until"] = time.time() + 120
        manager._save()
        with pytest.raises(PinError, match="locked"):
            manager.verify_pin("dev", "1234")

    def test_correct_pin_resets_attempts(self, manager):
        manager.set_pin("dev", "1234")
        try:
            manager.verify_pin("dev", "bad")
        except PinError:
            pass
        manager.verify_pin("dev", "1234")
        assert manager._data["dev"]["attempts"] == 0

    def test_data_persists_across_instances(self, tmp_dir):
        m1 = PinManager(tmp_dir)
        m1.set_pin("prod", "9999")
        m2 = PinManager(tmp_dir)
        assert m2.has_pin("prod") is True
        m2.verify_pin("prod", "9999")  # should not raise
