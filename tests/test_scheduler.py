"""Tests for envchain.scheduler."""

import json
import time
import pytest
from pathlib import Path

from envchain.scheduler import Scheduler, ScheduledAction


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def scheduler(tmp_dir):
    return Scheduler(tmp_dir)


@pytest.fixture
def sample_action():
    return ScheduledAction(
        profile_name="prod",
        action="activate",
        run_at=time.time() - 10,
    )


class TestScheduledAction:
    def test_to_dict_contains_required_keys(self, sample_action):
        d = sample_action.to_dict()
        assert "profile_name" in d
        assert "action" in d
        assert "run_at" in d

    def test_from_dict_roundtrip(self, sample_action):
        restored = ScheduledAction.from_dict(sample_action.to_dict())
        assert restored.profile_name == sample_action.profile_name
        assert restored.action == sample_action.action
        assert restored.run_at == sample_action.run_at

    def test_is_due_past_timestamp(self, sample_action):
        assert sample_action.is_due()

    def test_is_not_due_future_timestamp(self):
        future = ScheduledAction("dev", "expire", time.time() + 9999)
        assert not future.is_due()

    def test_repr_contains_profile_and_action(self, sample_action):
        r = repr(sample_action)
        assert "prod" in r
        assert "activate" in r


class TestScheduler:
    def test_add_and_list(self, scheduler, sample_action):
        scheduler.add(sample_action)
        assert len(scheduler.all_actions()) == 1

    def test_persist_across_instances(self, tmp_dir, sample_action):
        s1 = Scheduler(tmp_dir)
        s1.add(sample_action)
        s2 = Scheduler(tmp_dir)
        assert len(s2.all_actions()) == 1

    def test_remove_existing(self, scheduler, sample_action):
        scheduler.add(sample_action)
        result = scheduler.remove("prod", "activate")
        assert result is True
        assert scheduler.all_actions() == []

    def test_remove_nonexistent_returns_false(self, scheduler):
        assert scheduler.remove("ghost", "activate") is False

    def test_due_actions_returns_past_only(self, scheduler):
        past = ScheduledAction("a", "activate", time.time() - 5)
        future = ScheduledAction("b", "expire", time.time() + 5000)
        scheduler.add(past)
        scheduler.add(future)
        due = scheduler.due_actions()
        assert len(due) == 1
        assert due[0].profile_name == "a"

    def test_empty_schedule_file_returns_empty(self, tmp_dir):
        s = Scheduler(tmp_dir)
        assert s.all_actions() == []
