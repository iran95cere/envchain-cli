"""Tests for envchain.auditor module."""

import json
import pytest
from pathlib import Path

from envchain.auditor import AuditEvent, EnvAuditor


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def auditor(tmp_dir):
    return EnvAuditor(base_dir=tmp_dir)


class TestAuditEvent:
    def test_to_dict_contains_required_keys(self):
        event = AuditEvent(action="load", profile="dev", detail="exported 3 vars")
        d = event.to_dict()
        assert d["action"] == "load"
        assert d["profile"] == "dev"
        assert d["detail"] == "exported 3 vars"
        assert "timestamp" in d

    def test_from_dict_roundtrip(self):
        event = AuditEvent(action="save", profile="prod")
        restored = AuditEvent.from_dict(event.to_dict())
        assert restored.action == "save"
        assert restored.profile == "prod"
        assert restored.timestamp == event.timestamp

    def test_repr_includes_action_and_profile(self):
        event = AuditEvent(action="delete", profile="staging")
        text = repr(event)
        assert "delete" in text
        assert "staging" in text

    def test_repr_includes_detail_when_present(self):
        event = AuditEvent(action="init", profile="local", detail="created new")
        assert "created new" in repr(event)


class TestEnvAuditor:
    def test_record_creates_log_file(self, auditor, tmp_dir):
        auditor.record("init", "dev")
        log_path = Path(tmp_dir) / "audit.log"
        assert log_path.exists()

    def test_record_appends_valid_json_lines(self, auditor, tmp_dir):
        auditor.record("load", "dev", detail="3 vars")
        auditor.record("save", "prod")
        log_path = Path(tmp_dir) / "audit.log"
        lines = log_path.read_text().strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            data = json.loads(line)
            assert "action" in data
            assert "profile" in data

    def test_read_events_returns_all_when_no_filter(self, auditor):
        auditor.record("init", "dev")
        auditor.record("load", "prod")
        events = auditor.read_events()
        assert len(events) == 2

    def test_read_events_filters_by_profile(self, auditor):
        auditor.record("init", "dev")
        auditor.record("load", "prod")
        auditor.record("save", "dev")
        events = auditor.read_events(profile="dev")
        assert len(events) == 2
        assert all(e.profile == "dev" for e in events)

    def test_read_events_respects_limit(self, auditor):
        for i in range(10):
            auditor.record("load", "dev", detail=str(i))
        events = auditor.read_events(limit=5)
        assert len(events) == 5

    def test_read_events_returns_empty_when_no_log(self, auditor):
        events = auditor.read_events()
        assert events == []

    def test_clear_removes_log_file(self, auditor, tmp_dir):
        auditor.record("init", "dev")
        auditor.clear()
        log_path = Path(tmp_dir) / "audit.log"
        assert not log_path.exists()

    def test_clear_is_safe_when_no_log(self, auditor):
        auditor.clear()  # should not raise
