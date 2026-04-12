"""Tests for envchain.cli_notify."""
import pytest
from envchain.env_notify import NotificationBus, NotifyLevel
from envchain.cli_notify import NotifyCommand


@pytest.fixture
def bus():
    return NotificationBus()


@pytest.fixture
def cmd(bus):
    return NotifyCommand(bus)


@pytest.fixture
def populated_cmd(bus):
    bus.notify("startup complete", level=NotifyLevel.INFO, profile="dev")
    bus.notify("key rotated", level=NotifyLevel.WARNING, profile="prod")
    bus.notify("error occurred", level=NotifyLevel.ERROR, profile="dev")
    return NotifyCommand(bus)


class TestNotifyCommand:
    def test_show_history_empty_prints_message(self, cmd, capsys):
        cmd.show_history()
        out = capsys.readouterr().out
        assert "No notifications" in out

    def test_show_history_lists_entries(self, populated_cmd, capsys):
        populated_cmd.show_history()
        out = capsys.readouterr().out
        assert "startup complete" in out
        assert "key rotated" in out

    def test_show_history_filtered_by_profile(self, populated_cmd, capsys):
        populated_cmd.show_history(profile="dev")
        out = capsys.readouterr().out
        assert "startup complete" in out
        assert "key rotated" not in out

    def test_clear_prints_confirmation(self, populated_cmd, capsys):
        populated_cmd.clear()
        out = capsys.readouterr().out
        assert "cleared" in out.lower()

    def test_send_adds_to_history(self, cmd):
        cmd.send("test message", level="warning", profile="dev")
        assert len(cmd._bus.history()) == 1
        assert cmd._bus.history()[0].level == NotifyLevel.WARNING

    def test_send_invalid_level_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.send("msg", level="critical")

    def test_count_output(self, populated_cmd, capsys):
        populated_cmd.count()
        out = capsys.readouterr().out
        assert "3" in out

    def test_count_filtered_by_profile(self, populated_cmd, capsys):
        populated_cmd.count(profile="dev")
        out = capsys.readouterr().out
        assert "2" in out
