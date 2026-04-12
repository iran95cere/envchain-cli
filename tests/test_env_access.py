"""Tests for envchain.env_access."""
import pytest
from pathlib import Path

from envchain.env_access import AccessManager, AccessRule, AccessCheckResult


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def manager(tmp_dir):
    return AccessManager(tmp_dir)


class TestAccessRule:
    def test_to_dict_contains_required_keys(self):
        rule = AccessRule(profile="prod", allowed_users=["alice"], read_only=True)
        d = rule.to_dict()
        assert d["profile"] == "prod"
        assert d["allowed_users"] == ["alice"]
        assert d["read_only"] is True

    def test_from_dict_roundtrip(self):
        rule = AccessRule(profile="dev", denied_users=["bob"], read_only=False)
        restored = AccessRule.from_dict(rule.to_dict())
        assert restored.profile == rule.profile
        assert restored.denied_users == rule.denied_users
        assert restored.read_only == rule.read_only

    def test_from_dict_uses_defaults(self):
        rule = AccessRule.from_dict({"profile": "staging"})
        assert rule.allowed_users == []
        assert rule.denied_users == []
        assert rule.read_only is False

    def test_repr_contains_profile(self):
        rule = AccessRule(profile="prod")
        assert "prod" in repr(rule)


class TestAccessCheckResult:
    def test_bool_true_when_allowed(self):
        r = AccessCheckResult(allowed=True, reason="ok")
        assert bool(r) is True

    def test_bool_false_when_denied(self):
        r = AccessCheckResult(allowed=False, reason="denied")
        assert bool(r) is False

    def test_repr_contains_reason(self):
        r = AccessCheckResult(allowed=True, reason="access granted")
        assert "access granted" in repr(r)


class TestAccessManager:
    def test_no_rule_allows_any_user(self, manager):
        result = manager.check("prod", "alice")
        assert result.allowed is True

    def test_denied_user_is_blocked(self, manager):
        rule = AccessRule(profile="prod", denied_users=["mallory"])
        manager.set_rule(rule)
        result = manager.check("prod", "mallory")
        assert result.allowed is False

    def test_user_not_in_allowed_list_is_blocked(self, manager):
        rule = AccessRule(profile="prod", allowed_users=["alice"])
        manager.set_rule(rule)
        result = manager.check("prod", "bob")
        assert result.allowed is False

    def test_user_in_allowed_list_passes(self, manager):
        rule = AccessRule(profile="prod", allowed_users=["alice"])
        manager.set_rule(rule)
        result = manager.check("prod", "alice")
        assert result.allowed is True

    def test_read_only_blocks_write(self, manager):
        rule = AccessRule(profile="prod", read_only=True)
        manager.set_rule(rule)
        result = manager.check("prod", "alice", write=True)
        assert result.allowed is False

    def test_read_only_allows_read(self, manager):
        rule = AccessRule(profile="prod", read_only=True)
        manager.set_rule(rule)
        result = manager.check("prod", "alice", write=False)
        assert result.allowed is True

    def test_rules_persist_across_instances(self, tmp_dir):
        m1 = AccessManager(tmp_dir)
        m1.set_rule(AccessRule(profile="dev", allowed_users=["carol"]))
        m2 = AccessManager(tmp_dir)
        assert m2.get_rule("dev") is not None
        assert m2.get_rule("dev").allowed_users == ["carol"]

    def test_remove_rule(self, manager):
        manager.set_rule(AccessRule(profile="dev"))
        removed = manager.remove_rule("dev")
        assert removed is True
        assert manager.get_rule("dev") is None

    def test_remove_nonexistent_returns_false(self, manager):
        assert manager.remove_rule("ghost") is False

    def test_list_rules(self, manager):
        manager.set_rule(AccessRule(profile="a"))
        manager.set_rule(AccessRule(profile="b"))
        names = {r.profile for r in manager.list_rules()}
        assert names == {"a", "b"}
