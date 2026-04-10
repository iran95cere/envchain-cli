"""Tests for EnvRunner and RunResult."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from envchain.env_runner import EnvRunner, RunResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_storage(variables: dict | None = None, missing: bool = False):
    profile = MagicMock()
    profile.variables = variables or {"API_KEY": "secret", "DEBUG": "1"}

    storage = MagicMock()
    storage.load_profile.return_value = None if missing else profile
    return storage


# ---------------------------------------------------------------------------
# RunResult
# ---------------------------------------------------------------------------

class TestRunResult:
    def test_success_true_when_returncode_zero(self):
        r = RunResult(returncode=0, command=["echo"], profile_name="dev")
        assert r.success is True

    def test_success_false_when_nonzero(self):
        r = RunResult(returncode=1, command=["false"], profile_name="dev")
        assert r.success is False

    def test_injected_vars_defaults_empty(self):
        r = RunResult(returncode=0, command=["echo"], profile_name="dev")
        assert r.injected_vars == []


# ---------------------------------------------------------------------------
# EnvRunner
# ---------------------------------------------------------------------------

class TestEnvRunner:
    def test_run_injects_profile_vars(self, monkeypatch):
        storage = _make_storage({"HELLO": "world"})
        runner = EnvRunner(storage, "pass")

        captured_env = {}

        def fake_run(cmd, env):
            captured_env.update(env)
            return MagicMock(returncode=0)

        monkeypatch.setattr("envchain.env_runner.subprocess.run", fake_run)
        result = runner.run("dev", ["echo", "hi"])

        assert captured_env["HELLO"] == "world"
        assert result.success
        assert "HELLO" in result.injected_vars

    def test_run_raises_for_missing_profile(self):
        storage = _make_storage(missing=True)
        runner = EnvRunner(storage, "pass")

        with pytest.raises(KeyError, match="not found"):
            runner.run("ghost", ["echo"])

    def test_run_raises_for_empty_command(self):
        storage = _make_storage()
        runner = EnvRunner(storage, "pass")

        with pytest.raises(ValueError, match="empty"):
            runner.run("dev", [])

    def test_run_does_not_override_existing_by_default(self, monkeypatch):
        storage = _make_storage({"PATH": "/injected"})
        runner = EnvRunner(storage, "pass")

        captured_env = {}

        def fake_run(cmd, env):
            captured_env.update(env)
            return MagicMock(returncode=0)

        monkeypatch.setattr("envchain.env_runner.subprocess.run", fake_run)
        monkeypatch.setenv("PATH", "/original")

        runner.run("dev", ["echo"], override_existing=False)
        assert captured_env["PATH"] == "/original"

    def test_run_overrides_when_flag_set(self, monkeypatch):
        storage = _make_storage({"MY_VAR": "new"})
        runner = EnvRunner(storage, "pass")

        captured_env = {}

        def fake_run(cmd, env):
            captured_env.update(env)
            return MagicMock(returncode=0)

        monkeypatch.setattr("envchain.env_runner.subprocess.run", fake_run)
        monkeypatch.setenv("MY_VAR", "old")

        runner.run("dev", ["echo"], override_existing=True)
        assert captured_env["MY_VAR"] == "new"

    def test_extra_env_is_merged(self, monkeypatch):
        storage = _make_storage({"A": "1"})
        runner = EnvRunner(storage, "pass")

        captured_env = {}

        def fake_run(cmd, env):
            captured_env.update(env)
            return MagicMock(returncode=0)

        monkeypatch.setattr("envchain.env_runner.subprocess.run", fake_run)
        runner.run("dev", ["echo"], extra_env={"EXTRA": "yes"})
        assert captured_env["EXTRA"] == "yes"
