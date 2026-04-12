"""Tests for cli_audit_policy module."""
import sys
import pytest
from envchain.env_audit_policy import AuditPolicyManager, PolicyRule
from envchain.cli_audit_policy import AuditPolicyCommand


@pytest.fixture
def manager() -> AuditPolicyManager:
    return AuditPolicyManager()


@pytest.fixture
def cmd(manager) -> AuditPolicyCommand:
    return AuditPolicyCommand(manager=manager)


class TestAuditPolicyCommand:
    def test_add_valid_rule_prints_ok(self, cmd, capsys):
        cmd.add("dev", "write")
        out = capsys.readouterr().out
        assert "[ok]" in out

    def test_add_invalid_action_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.add("dev", "explode")

    def test_add_invalid_action_prints_error(self, cmd, capsys):
        with pytest.raises(SystemExit):
            cmd.add("dev", "explode")
        err = capsys.readouterr().err
        assert "[error]" in err

    def test_remove_existing_rule(self, cmd, manager, capsys):
        manager.add_rule(PolicyRule(profile="dev", action="write"))
        cmd.remove("dev", "write")
        out = capsys.readouterr().out
        assert "[ok]" in out

    def test_remove_nonexistent_rule_warns(self, cmd, capsys):
        cmd.remove("dev", "write")
        out = capsys.readouterr().out
        assert "[warn]" in out

    def test_list_rules_empty(self, cmd, capsys):
        cmd.list_rules()
        out = capsys.readouterr().out
        assert "No audit policy rules" in out

    def test_list_rules_shows_entries(self, cmd, manager, capsys):
        manager.add_rule(PolicyRule(profile="prod", action="delete", require_reason=True))
        cmd.list_rules()
        out = capsys.readouterr().out
        assert "prod" in out
        assert "delete" in out

    def test_check_no_violations_prints_ok(self, cmd, capsys):
        cmd.check("dev", "read")
        out = capsys.readouterr().out
        assert "[ok]" in out

    def test_check_violation_exits(self, cmd, manager):
        manager.add_rule(PolicyRule(profile="prod", action="delete", require_reason=True))
        with pytest.raises(SystemExit):
            cmd.check("prod", "delete")

    def test_check_violation_prints_to_stderr(self, cmd, manager, capsys):
        manager.add_rule(PolicyRule(profile="prod", action="delete", require_reason=True))
        with pytest.raises(SystemExit):
            cmd.check("prod", "delete")
        err = capsys.readouterr().err
        assert "[violation]" in err
