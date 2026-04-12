"""Pipeline: chain multiple env transformations in sequence."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class PipelineStep:
    name: str
    transform: Callable[[Dict[str, str]], Dict[str, str]]
    enabled: bool = True

    def __repr__(self) -> str:
        status = "on" if self.enabled else "off"
        return f"<PipelineStep name={self.name!r} [{status}]>"


@dataclass
class PipelineResult:
    final_vars: Dict[str, str]
    steps_applied: List[str] = field(default_factory=list)
    steps_skipped: List[str] = field(default_factory=list)
    errors: Dict[str, str] = field(default_factory=dict)

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)

    @property
    def applied_count(self) -> int:
        return len(self.steps_applied)

    def __repr__(self) -> str:
        return (
            f"<PipelineResult applied={self.applied_count} "
            f"skipped={len(self.steps_skipped)} errors={len(self.errors)}>"
        )


class EnvPipeline:
    """Runs a sequence of transformation steps over an env var dict."""

    def __init__(self) -> None:
        self._steps: List[PipelineStep] = []

    def add_step(
        self,
        name: str,
        transform: Callable[[Dict[str, str]], Dict[str, str]],
        enabled: bool = True,
    ) -> "EnvPipeline":
        if not name or not name.strip():
            raise ValueError("Step name must not be empty.")
        if any(s.name == name for s in self._steps):
            raise ValueError(f"Step {name!r} already registered.")
        self._steps.append(PipelineStep(name=name, transform=transform, enabled=enabled))
        return self

    def remove_step(self, name: str) -> bool:
        before = len(self._steps)
        self._steps = [s for s in self._steps if s.name != name]
        return len(self._steps) < before

    def enable_step(self, name: str) -> None:
        for step in self._steps:
            if step.name == name:
                step.enabled = True
                return
        raise KeyError(f"Step {name!r} not found.")

    def disable_step(self, name: str) -> None:
        for step in self._steps:
            if step.name == name:
                step.enabled = False
                return
        raise KeyError(f"Step {name!r} not found.")

    def run(self, vars_: Dict[str, str]) -> PipelineResult:
        current = dict(vars_)
        applied: List[str] = []
        skipped: List[str] = []
        errors: Dict[str, str] = {}

        for step in self._steps:
            if not step.enabled:
                skipped.append(step.name)
                continue
            try:
                current = step.transform(current)
                applied.append(step.name)
            except Exception as exc:  # noqa: BLE001
                errors[step.name] = str(exc)
                skipped.append(step.name)

        return PipelineResult(
            final_vars=current,
            steps_applied=applied,
            steps_skipped=skipped,
            errors=errors,
        )

    @property
    def step_names(self) -> List[str]:
        return [s.name for s in self._steps]
