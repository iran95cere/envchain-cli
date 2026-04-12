"""Tests for env_audit_policy module."""
import pytest
from envchain.env_audit_policy import AuditPolicyManager, PolicyRule, PolicyViolation


@pytest.fixture
def manager() -> AuditPolicyManager:
    return AuditPolicyManager()


class TestPolicyRule:
    def test_to_dict_contains_required_keys(self):
        rule = PolicyRule(profile="dev", action="write")
        d = rule.to_dict()
        assert "profile" in d
        assert "action" in d
        assert "require_reason" in d
        assert "max_value_length" in d

    def test_from_dict_roundtrip(self):
        rule = PolicyRule(profile="prod", action="read", require_reason=True, max_value_length=128)
        restored = PolicyRule.from_dict(rule.to_dict())
        assert restored.profile == rule.profile
        assert restored.action == rule.action
        assert restored.require_reason == rule.require_reason
        assert restored.max_value_length == rule.max_value_length

    def test_repr_contains_profile_and_action(self):
        rule = PolicyRule(profile="staging", action="delete")
        assert "staging" in repr(rule)
        assert "delete" in repr(rule)

    def test_from_dict_defaults(self):
        rule = PolicyRule.from_dict({"profile": "dev", "action": "read"})
        assert rule.require_reason is False
        assert rule.max_value_length is None


class TestAuditPolicyManager:
    def test_add_and_list_rules(self, manager):
        rule = PolicyRule(profile="dev", action="write")
        manager.add_rule(rule)
        assert len(manager.all_rules()) == 1

    def test_rules_for_filters_correctly(self, manager):
        manager.add_rule(PolicyRule(profile="dev", action="write"))
        manager.add_rule(PolicyRule(profile="dev", action="read"))
        manager.add_rule(PolicyRule(profile="prod", action="write"))
        assert len(manager.rules_for("dev", "write")) == 1
        assert len(manager.rules_for("dev", "read")) == 1
        assert len(manager.rules_for("prod", "write")) == 1
        assert len(manager.rules_for("prod", "read")) == 0

    def test_remove_existing_rule(self, manager):
        manager.add_rule(PolicyRule(profile="dev", action="write"))
        removed = manager.remove_rule("dev", "write")
        assert removed is True
        assert len(manager.all_rules()) == 0

    def test_remove_nonexistent_rule_returns_false(self, manager):
        removed = manager.remove_rule("dev", "write")
        assert removed is False

    def test_check_no_violations_when_no_rules(self, manager):
        violations = manager.check("dev", "write", value="hello")
        assert violations == []

    def test_check_require_reason_violation(self, manager):
        manager.add_rule(PolicyRule(profile="prod", action="delete", require_reason=True))
        violations = manager.check("prod", "delete")
        assert len(violations) == 1
        assert "reason" in violations[0].message

    def test_check_require_reason_passes_with_reason(self, manager):
        manager.add_rule(PolicyRule(profile="prod", action="delete", require_reason=True))
        violations = manager.check("prod", "delete", reason="cleanup")
        assert violations == []

    def test_check_max_value_length_violation(self, manager):
        manager.add_rule(PolicyRule(profile="dev", action="write", max_value_length=10))
        violations = manager.check("dev", "write", value="x" * 20)
        assert len(violations) == 1
        assert "length" in violations[0].message

    def test_check_max_value_length_passes(self, manager):
        manager.add_rule(PolicyRule(profile="dev", action="write", max_value_length=10))
        violations = manager.check("dev", "write", value="short")
        assert violations == []

    def test_policy_violation_repr(self):
        rule = PolicyRule(profile="dev", action="write")
        v = PolicyViolation(rule=rule, message="test violation")
        assert "test violation" in repr(v)
