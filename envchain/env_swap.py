"""Swap the values of two environment variables within a profile."""
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class SwapResult:
    var_a: str
    var_b: str
    value_a: str
    value_b: str
    success: bool = True
    error: Optional[str] = None

    def __repr__(self) -> str:
        if self.success:
            return f"<SwapResult {self.var_a!r} <-> {self.var_b!r} ok>"
        return f"<SwapResult {self.var_a!r} <-> {self.var_b!r} error={self.error!r}>"


@dataclass
class SwapReport:
    results: list = field(default_factory=list)

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.results if r.success)

    @property
    def failure_count(self) -> int:
        return sum(1 for r in self.results if not r.success)

    @property
    def has_failures(self) -> bool:
        return self.failure_count > 0

    def __repr__(self) -> str:
        return (
            f"<SwapReport swaps={len(self.results)} "
            f"ok={self.success_count} fail={self.failure_count}>"
        )


class EnvSwapper:
    """Swap values of variable pairs within a dict of env vars."""

    def swap(self, vars: Dict[str, str], var_a: str, var_b: str) -> SwapResult:
        """Swap values of var_a and var_b in-place; returns a SwapResult."""
        if var_a not in vars:
            return SwapResult(
                var_a=var_a, var_b=var_b,
                value_a="", value_b="",
                success=False,
                error=f"Variable {var_a!r} not found",
            )
        if var_b not in vars:
            return SwapResult(
                var_a=var_a, var_b=var_b,
                value_a="", value_b="",
                success=False,
                error=f"Variable {var_b!r} not found",
            )
        val_a = vars[var_a]
        val_b = vars[var_b]
        vars[var_a] = val_b
        vars[var_b] = val_a
        return SwapResult(var_a=var_a, var_b=var_b, value_a=val_a, value_b=val_b)

    def swap_many(
        self, vars: Dict[str, str], pairs: list
    ) -> SwapReport:
        """Swap multiple pairs; each pair is a (var_a, var_b) tuple."""
        report = SwapReport()
        for var_a, var_b in pairs:
            result = self.swap(vars, var_a, var_b)
            report.results.append(result)
        return report
