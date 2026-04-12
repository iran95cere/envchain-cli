"""CLI commands for env pipeline management."""
from __future__ import annotations

from typing import Dict, List, Optional

from envchain.env_pipeline import EnvPipeline, PipelineResult


class PipelineCommand:
    """High-level CLI wrapper around EnvPipeline."""

    def __init__(self, pipeline: Optional[EnvPipeline] = None) -> None:
        self._pipeline = pipeline or EnvPipeline()

    # ------------------------------------------------------------------
    # Informational
    # ------------------------------------------------------------------

    def list_steps(self) -> None:
        steps = self._pipeline._steps
        if not steps:
            print("No pipeline steps registered.")
            return
        for step in steps:
            status = "enabled" if step.enabled else "disabled"
            print(f"  {step.name}  [{status}]")

    # ------------------------------------------------------------------
    # Step management
    # ------------------------------------------------------------------

    def enable(self, name: str) -> None:
        try:
            self._pipeline.enable_step(name)
            print(f"Step '{name}' enabled.")
        except KeyError as exc:
            print(f"Error: {exc}")
            raise SystemExit(1) from exc

    def disable(self, name: str) -> None:
        try:
            self._pipeline.disable_step(name)
            print(f"Step '{name}' disabled.")
        except KeyError as exc:
            print(f"Error: {exc}")
            raise SystemExit(1) from exc

    def remove(self, name: str) -> None:
        removed = self._pipeline.remove_step(name)
        if removed:
            print(f"Step '{name}' removed.")
        else:
            print(f"Step '{name}' not found.")
            raise SystemExit(1)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def run(self, vars_: Dict[str, str]) -> PipelineResult:
        result = self._pipeline.run(vars_)
        print(f"Pipeline complete: {result.applied_count} step(s) applied.")
        if result.steps_skipped:
            print(f"  Skipped: {', '.join(result.steps_skipped)}")
        if result.errors:
            for step, msg in result.errors.items():
                print(f"  Error in '{step}': {msg}")
        return result
