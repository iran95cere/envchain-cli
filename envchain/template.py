"""Template rendering for environment variable sets."""
from __future__ import annotations

import re
from typing import Dict, Optional


class TemplateRenderError(Exception):
    """Raised when a template cannot be rendered."""


class EnvTemplate:
    """Renders templates by substituting ${VAR} or $VAR placeholders."""

    _PLACEHOLDER_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")

    def __init__(self, strict: bool = True) -> None:
        """Create a template renderer.

        Args:
            strict: If True, raise an error for missing variables.
                    If False, leave unresolved placeholders as-is.
        """
        self.strict = strict

    def render(self, template: str, variables: Dict[str, str]) -> str:
        """Substitute placeholders in *template* using *variables*.

        Args:
            template: A string potentially containing ``${VAR}`` or ``$VAR``.
            variables: Mapping of variable names to their values.

        Returns:
            The rendered string.

        Raises:
            TemplateRenderError: If *strict* is True and a placeholder is
                missing from *variables*.
        """
        missing: list[str] = []

        def _replace(match: re.Match) -> str:  # type: ignore[type-arg]
            name = match.group(1) or match.group(2)
            if name in variables:
                return variables[name]
            if self.strict:
                missing.append(name)
                return match.group(0)
            return match.group(0)

        result = self._PLACEHOLDER_RE.sub(_replace, template)

        if missing:
            raise TemplateRenderError(
                f"Template references undefined variable(s): {', '.join(sorted(missing))}"
            )
        return result

    def collect_placeholders(self, template: str) -> list[str]:
        """Return a sorted, deduplicated list of placeholder names in *template*."""
        names = {
            m.group(1) or m.group(2)
            for m in self._PLACEHOLDER_RE.finditer(template)
        }
        return sorted(names)

    def render_dict(
        self, templates: Dict[str, str], variables: Dict[str, str]
    ) -> Dict[str, str]:
        """Render every value in *templates* using *variables*."""
        return {key: self.render(value, variables) for key, value in templates.items()}
