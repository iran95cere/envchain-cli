"""Tests for envchain.env_notify."""
import pytest
from envchain.env_notify import Notification, NotificationBus, NotifyLevel


@pytest.fixture
def bus():
    return NotificationBus()


class TestNotification:
    def test_to_dict_contains_required_keys(self):
        n = Notification(message="hello", level=NotifyLevel.WARNING, profile="dev")
        d = n.to_dict()
        assert d["message"] == "hello"
        assert d["level"] == "warning"
        assert d["profile"] == "dev"
        assert "timestamp" in d

    def test_from_dict_roundtrip(self):
        n = Notification(message="test", level=NotifyLevel.ERROR, profile="prod")
        n2 = Notification.from_dict(n.to_dict())
        assert n2.message == n.message
        assert n2.level == n.level
        assert n2.profile == n.profile

    def test_repr_contains_message(self):
        n = Notification(message="boom", level=NotifyLevel.ERROR)
        assert "boom" in repr(n)
        assert "error" in repr(n)

    def test_default_level_is_info(self):
        n = Notification(message="hi")
        assert n.level == NotifyLevel.INFO


class TestNotificationBus:
    def test_publish_calls_handler(self, bus):
        received = []
        bus.subscribe(received.append)
        bus.notify("msg")
        assert len(received) == 1
        assert received[0].message == "msg"

    def test_unsubscribe_stops_calls(self, bus):
        received = []
        bus.subscribe(received.append)
        bus.unsubscribe(received.append)
        bus.notify("msg")
        assert len(received) == 0

    def test_history_stores_notifications(self, bus):
        bus.notify("a")
        bus.notify("b")
        assert len(bus.history()) == 2

    def test_history_filtered_by_profile(self, bus):
        bus.notify("a", profile="dev")
        bus.notify("b", profile="prod")
        assert len(bus.history(profile="dev")) == 1
        assert bus.history(profile="dev")[0].message == "a"

    def test_clear_history_empties_log(self, bus):
        bus.notify("x")
        bus.clear_history()
        assert bus.history() == []

    def test_notify_returns_notification(self, bus):
        n = bus.notify("hello", level=NotifyLevel.WARNING, profile="staging")
        assert isinstance(n, Notification)
        assert n.level == NotifyLevel.WARNING

    def test_multiple_handlers(self, bus):
        log1, log2 = [], []
        bus.subscribe(log1.append)
        bus.subscribe(log2.append)
        bus.notify("shared")
        assert len(log1) == 1
        assert len(log2) == 1
