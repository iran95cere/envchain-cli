"""Tests for envchain.env_pipeline."""
from __future__ import annotations

import pytest

from envchain.env_pipeline import EnvPipeline, PipelineResult, PipelineStep


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def pipeline() -> EnvPipeline:
    return EnvPipeline()


SAMPLE_VARS = {"FOO": "bar", "BAZ": "qux"}


# ---------------------------------------------------------------------------
# PipelineStep
# ---------------------------------------------------------------------------

class TestPipelineStep:
    def test_repr_enabled(self):
        step = PipelineStep(name="upper", transform=lambda v: v, enabled=True)
        assert "on" in repr(step)
        assert "upper" in repr(step)

    def test_repr_disabled(self):
        step = PipelineStep(name="lower", transform=lambda v: v, enabled=False)
        assert "off" in repr(step)


# ---------------------------------------------------------------------------
# PipelineResult
# ---------------------------------------------------------------------------

class TestPipelineResult:
    def test_has_errors_false_when_empty(self):
        r = PipelineResult(final_vars={})
        assert not r.has_errors

    def test_has_errors_true_when_present(self):
        r = PipelineResult(final_vars={}, errors={"step1": "boom"})
        assert r.has_errors

    def test_applied_count(self):
        r = PipelineResult(final_vars={}, steps_applied=["a", "b"])
        assert r.applied_count == 2

    def test_repr_contains_counts(self):
        r = PipelineResult(
            final_vars={},
            steps_applied=["a"],
            steps_skipped=["b"],
            errors={"c": "err"},
        )
        assert "applied=1" in repr(r)
        assert "skipped=1" in repr(r)
        assert "errors=1" in repr(r)


# ---------------------------------------------------------------------------
# EnvPipeline
# ---------------------------------------------------------------------------

class TestEnvPipeline:
    def test_add_step_and_list(self, pipeline):
        pipeline.add_step("upper", lambda v: {k: val.upper() for k, val in v.items()})
        assert "upper" in pipeline.step_names

    def test_add_duplicate_step_raises(self, pipeline):
        pipeline.add_step("s1", lambda v: v)
        with pytest.raises(ValueError, match="already registered"):
            pipeline.add_step("s1", lambda v: v)

    def test_add_empty_name_raises(self, pipeline):
        with pytest.raises(ValueError):
            pipeline.add_step("", lambda v: v)

    def test_run_applies_transform(self, pipeline):
        pipeline.add_step("upper", lambda v: {k: val.upper() for k, val in v.items()})
        result = pipeline.run({"key": "value"})
        assert result.final_vars["key"] == "VALUE"
        assert "upper" in result.steps_applied

    def test_run_chained_steps(self, pipeline):
        pipeline.add_step("prefix", lambda v: {f"X_{k}": val for k, val in v.items()})
        pipeline.add_step("upper", lambda v: {k: val.upper() for k, val in v.items()})
        result = pipeline.run({"foo": "bar"})
        assert "X_foo" in result.final_vars
        assert result.final_vars["X_foo"] == "BAR"

    def test_disabled_step_is_skipped(self, pipeline):
        pipeline.add_step("upper", lambda v: {k: val.upper() for k, val in v.items()}, enabled=False)
        result = pipeline.run({"key": "value"})
        assert result.final_vars["key"] == "value"
        assert "upper" in result.steps_skipped

    def test_enable_disable_step(self, pipeline):
        pipeline.add_step("step", lambda v: v, enabled=False)
        pipeline.enable_step("step")
        assert pipeline._steps[0].enabled is True
        pipeline.disable_step("step")
        assert pipeline._steps[0].enabled is False

    def test_enable_unknown_step_raises(self, pipeline):
        with pytest.raises(KeyError):
            pipeline.enable_step("ghost")

    def test_remove_step(self, pipeline):
        pipeline.add_step("s", lambda v: v)
        removed = pipeline.remove_step("s")
        assert removed is True
        assert "s" not in pipeline.step_names

    def test_remove_nonexistent_returns_false(self, pipeline):
        assert pipeline.remove_step("nope") is False

    def test_error_in_step_captured(self, pipeline):
        def bad_step(v):
            raise RuntimeError("explosion")

        pipeline.add_step("bad", bad_step)
        result = pipeline.run({"k": "v"})
        assert "bad" in result.errors
        assert result.has_errors

    def test_fluent_add_step(self, pipeline):
        ret = pipeline.add_step("s", lambda v: v)
        assert ret is pipeline
