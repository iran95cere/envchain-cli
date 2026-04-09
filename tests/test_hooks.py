"""Tests for envchain.hooks."""

import pytest

from envchain.hooks import HookEvent, HookResult, HookRunner


@pytest.fixture()
def runner() -> HookRunner:
    return HookRunner()


# ---------------------------------------------------------------------------
# HookResult
# ---------------------------------------------------------------------------

class TestHookResult:
    def test_repr_success(self):
        r = HookResult(event=HookEvent.POST_LOAD, profile_name="dev", success=True)
        assert "ok" in repr(r)
        assert "post_load" in repr(r)

    def test_repr_failure(self):
        r = HookResult(event=HookEvent.PRE_SAVE, profile_name="prod", success=False)
        assert "failed" in repr(r)


# ---------------------------------------------------------------------------
# HookRunner — callable hooks
# ---------------------------------------------------------------------------

class TestCallableHooks:
    def test_callable_hook_is_invoked(self, runner):
        called_with = []
        runner.register_callable(HookEvent.POST_LOAD, lambda p: called_with.append(p))
        results = runner.run(HookEvent.POST_LOAD, "dev")
        assert called_with == ["dev"]
        assert results[0].success is True

    def test_callable_hook_failure_captured(self, runner):
        def bad_hook(profile):
            raise RuntimeError("boom")

        runner.register_callable(HookEvent.PRE_SAVE, bad_hook)
        results = runner.run(HookEvent.PRE_SAVE, "staging")
        assert results[0].success is False
        assert "boom" in results[0].error

    def test_register_non_callable_raises(self, runner):
        with pytest.raises(TypeError):
            runner.register_callable(HookEvent.POST_LOAD, "not_a_function")  # type: ignore

    def test_multiple_callable_hooks(self, runner):
        log = []
        runner.register_callable(HookEvent.POST_LOAD, lambda p: log.append("a"))
        runner.register_callable(HookEvent.POST_LOAD, lambda p: log.append("b"))
        runner.run(HookEvent.POST_LOAD, "dev")
        assert log == ["a", "b"]


# ---------------------------------------------------------------------------
# HookRunner — shell hooks
# ---------------------------------------------------------------------------

class TestShellHooks:
    def test_shell_hook_success(self, runner):
        runner.register_shell(HookEvent.POST_LOAD, "echo hello")
        results = runner.run(HookEvent.POST_LOAD, "dev")
        assert results[0].success is True
        assert results[0].output == "hello"

    def test_shell_hook_failure(self, runner):
        runner.register_shell(HookEvent.PRE_LOAD, "exit 1")
        results = runner.run(HookEvent.PRE_LOAD, "dev")
        assert results[0].success is False

    def test_register_empty_shell_command_raises(self, runner):
        with pytest.raises(ValueError):
            runner.register_shell(HookEvent.POST_SAVE, "   ")


# ---------------------------------------------------------------------------
# HookRunner — clear
# ---------------------------------------------------------------------------

class TestClear:
    def test_clear_specific_event(self, runner):
        log = []
        runner.register_callable(HookEvent.POST_LOAD, lambda p: log.append(p))
        runner.register_callable(HookEvent.PRE_SAVE, lambda p: log.append(p))
        runner.clear(HookEvent.POST_LOAD)
        runner.run(HookEvent.POST_LOAD, "dev")
        runner.run(HookEvent.PRE_SAVE, "dev")
        assert log == ["dev"]  # only PRE_SAVE ran

    def test_clear_all_events(self, runner):
        log = []
        for event in HookEvent:
            runner.register_callable(event, lambda p: log.append(p))
        runner.clear()
        for event in HookEvent:
            runner.run(event, "dev")
        assert log == []

    def test_run_returns_empty_when_no_hooks(self, runner):
        results = runner.run(HookEvent.POST_SAVE, "prod")
        assert results == []
