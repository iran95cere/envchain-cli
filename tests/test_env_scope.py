"""Tests for envchain.env_scope and envchain.cli_scope."""
from __future__ import annotations

import json
import pytest
from pathlib import Path

from envchain.env_scope import EnvScope, ScopeRule
from envchain.cli_scope import ScopeCommand


# ---------------------------------------------------------------------------
# ScopeRule
# ---------------------------------------------------------------------------

class TestScopeRule:
    def test_to_dict_contains_required_keys(self):
        rule = ScopeRule(context="ci", allowed=["CI_TOKEN"], denied=["SECRET"])
        d = rule.to_dict()
        assert d["context"] == "ci"
        assert d["allowed"] == ["CI_TOKEN"]
        assert d["denied"] == ["SECRET"]

    def test_from_dict_roundtrip(self):
        rule = ScopeRule(context="prod", allowed=["DB_URL"], denied=[])
        assert ScopeRule.from_dict(rule.to_dict()).context == "prod"

    def test_repr_contains_context(self):
        rule = ScopeRule(context="local")
        assert "local" in repr(rule)


# ---------------------------------------------------------------------------
# EnvScope
# ---------------------------------------------------------------------------

@pytest.fixture
def scope():
    return EnvScope()


VARS = {"DB_URL": "postgres://", "SECRET": "s3cr3t", "DEBUG": "1"}


class TestEnvScope:
    def test_apply_no_rule_returns_all(self, scope):
        assert scope.apply(VARS, "unknown") == VARS

    def test_apply_allowed_whitelist(self, scope):
        scope.add_rule(ScopeRule(context="ci", allowed=["DB_URL"]))
        result = scope.apply(VARS, "ci")
        assert result == {"DB_URL": "postgres://"}

    def test_apply_denied_removes_key(self, scope):
        scope.add_rule(ScopeRule(context="ci", denied=["SECRET"]))
        result = scope.apply(VARS, "ci")
        assert "SECRET" not in result
        assert "DB_URL" in result

    def test_add_rule_replaces_existing(self, scope):
        scope.add_rule(ScopeRule(context="ci", allowed=["A"]))
        scope.add_rule(ScopeRule(context="ci", allowed=["B"]))
        assert scope.get_rule("ci").allowed == ["B"]

    def test_remove_rule_returns_true(self, scope):
        scope.add_rule(ScopeRule(context="ci"))
        assert scope.remove_rule("ci") is True

    def test_remove_nonexistent_returns_false(self, scope):
        assert scope.remove_rule("ghost") is False

    def test_list_contexts(self, scope):
        scope.add_rule(ScopeRule(context="a"))
        scope.add_rule(ScopeRule(context="b"))
        assert set(scope.list_contexts()) == {"a", "b"}


# ---------------------------------------------------------------------------
# ScopeCommand (CLI layer)
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_dir


@pytest.fixture
def cmd(tmp_path):
    return ScopeCommand(base_dir=str(tmp_path))


class TestScopeCommand:
    def test_add_persists_rule(self, cmd, tmp_path):
        cmd.add("ci", ["TOKEN"], [])
        data = json.loads((tmp_path / ".envchain_scopes.json").read_text())
        assert any(r["context"] == "ci" for r in data["rules"])

    def test_remove_existing_rule(self, cmd):
        cmd.add("ci", [], [])
        cmd.remove("ci")  # should not raise

    def test_remove_missing_rule_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.remove("nonexistent")

    def test_apply_delegates_to_scope(self, cmd):
        cmd.add("prod", ["DB_URL"], [])
        result = cmd.apply("prod", {"DB_URL": "x", "SECRET": "y"})
        assert result == {"DB_URL": "x"}

    def test_show_no_rules_prints_message(self, cmd, capsys):
        cmd.show()
        out = capsys.readouterr().out
        assert "No scope rules" in out
