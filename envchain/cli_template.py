"""CLI command for rendering templates against a profile's variables."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from envchain.template import EnvTemplate, TemplateRenderError


class TemplateCommand:
    """Render a template file using variables from a loaded profile."""

    def __init__(self, variables: dict[str, str]) -> None:
        self._variables = variables

    def run(
        self,
        template_path: str,
        output_path: Optional[str] = None,
        strict: bool = True,
    ) -> int:
        """Read *template_path*, render it, and write to *output_path* (or stdout).

        Returns:
            0 on success, 1 on error.
        """
        path = Path(template_path)
        if not path.exists():
            print(f"error: template file not found: {template_path}", file=sys.stderr)
            return 1

        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"error: cannot read template: {exc}", file=sys.stderr)
            return 1

        renderer = EnvTemplate(strict=strict)
        try:
            rendered = renderer.render(content, self._variables)
        except TemplateRenderError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

        if output_path:
            try:
                Path(output_path).write_text(rendered, encoding="utf-8")
                print(f"Written to {output_path}")
            except OSError as exc:
                print(f"error: cannot write output: {exc}", file=sys.stderr)
                return 1
        else:
            sys.stdout.write(rendered)

        return 0

    def list_placeholders(self, template_path: str) -> int:
        """Print all placeholder names found in *template_path*."""
        path = Path(template_path)
        if not path.exists():
            print(f"error: template file not found: {template_path}", file=sys.stderr)
            return 1
        content = path.read_text(encoding="utf-8")
        renderer = EnvTemplate(strict=False)
        placeholders = renderer.collect_placeholders(content)
        if placeholders:
            for name in placeholders:
                print(name)
        else:
            print("(no placeholders found)")
        return 0
