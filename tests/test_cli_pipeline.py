"""Tests for envchain.cli_pipeline."""
from __future__ import annotations

import pytest

from envchain.cli_pipeline import PipelineCommand
from envchain.env_pipeline import EnvPipeline


@pytest.fixture()
def pipeline() -> EnvPipeline:
    p = EnvPipeline()
    p.add_step("upper", lambda v: {k: val.upper() for k, val in v.items()})
    p.add_step("noop", lambda v: v, enabled=False)
    return p


@pytest.fixture()
def cmd(pipeline) -> PipelineCommand:
    return PipelineCommand(pipeline=pipeline)


class TestPipelineCommand:
    def test_list_steps_prints_names(self, cmd, capsys):
        cmd.list_steps()
        out = capsys.readouterr().out
        assert "upper" in out
        assert "noop" in out

    def test_list_steps_enabled_status(self, cmd, capsys):
        cmd.list_steps()
        out = capsys.readouterr().out
        assert "enabled" in out
        assert "disabled" in out

    def test_list_steps_empty_pipeline(self, capsys):
        empty_cmd = PipelineCommand(pipeline=EnvPipeline())
        empty_cmd.list_steps()
        out = capsys.readouterr().out
        assert "No pipeline steps" in out

    def test_enable_step(self, cmd, capsys):
        cmd.enable("noop")
        out = capsys.readouterr().out
        assert "enabled" in out

    def test_disable_step(self, cmd, capsys):
        cmd.disable("upper")
        out = capsys.readouterr().out
        assert "disabled" in out

    def test_enable_unknown_step_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.enable("ghost")

    def test_disable_unknown_step_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.disable("ghost")

    def test_remove_existing_step(self, cmd, capsys):
        cmd.remove("noop")
        out = capsys.readouterr().out
        assert "removed" in out

    def test_remove_nonexistent_step_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.remove("ghost")

    def test_run_returns_result(self, cmd):
        result = cmd.run({"key": "value"})
        assert result.final_vars["key"] == "VALUE"

    def test_run_prints_summary(self, cmd, capsys):
        cmd.run({"a": "b"})
        out = capsys.readouterr().out
        assert "Pipeline complete" in out

    def test_run_prints_skipped(self, cmd, capsys):
        cmd.run({"a": "b"})
        out = capsys.readouterr().out
        assert "Skipped" in out
