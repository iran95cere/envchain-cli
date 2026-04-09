"""Tests for envchain.template and envchain.cli_template."""
from __future__ import annotations

import pytest
from pathlib import Path

from envchain.template import EnvTemplate, TemplateRenderError
from envchain.cli_template import TemplateCommand


# ---------------------------------------------------------------------------
# EnvTemplate unit tests
# ---------------------------------------------------------------------------

@pytest.fixture
def renderer() -> EnvTemplate:
    return EnvTemplate(strict=True)


def test_render_curly_brace_syntax(renderer):
    result = renderer.render("Hello, ${NAME}!", {"NAME": "World"})
    assert result == "Hello, World!"


def test_render_dollar_syntax(renderer):
    result = renderer.render("Hello, $NAME!", {"NAME": "Alice"})
    assert result == "Hello, Alice!"


def test_render_multiple_placeholders(renderer):
    result = renderer.render("${A} + ${B} = ${C}", {"A": "1", "B": "2", "C": "3"})
    assert result == "1 + 2 = 3"


def test_render_missing_strict_raises(renderer):
    with pytest.raises(TemplateRenderError, match="MISSING"):
        renderer.render("value=${MISSING}", {})


def test_render_missing_non_strict_leaves_placeholder():
    r = EnvTemplate(strict=False)
    result = r.render("value=${MISSING}", {})
    assert result == "value=${MISSING}"


def test_collect_placeholders_deduplicates(renderer):
    placeholders = renderer.collect_placeholders("${A} $B ${A} $C")
    assert placeholders == ["A", "B", "C"]


def test_collect_placeholders_empty(renderer):
    assert renderer.collect_placeholders("no placeholders here") == []


def test_render_dict(renderer):
    templates = {"URL": "http://${HOST}:${PORT}", "NAME": "$APP"}
    variables = {"HOST": "localhost", "PORT": "8080", "APP": "myapp"}
    result = renderer.render_dict(templates, variables)
    assert result == {"URL": "http://localhost:8080", "NAME": "myapp"}


# ---------------------------------------------------------------------------
# TemplateCommand integration tests
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_template(tmp_path: Path):
    """Returns a helper that writes a template file and returns its path."""
    def _write(content: str) -> str:
        p = tmp_path / "template.txt"
        p.write_text(content, encoding="utf-8")
        return str(p)
    return _write


def test_cli_template_renders_to_stdout(tmp_template, capsys):
    cmd = TemplateCommand({"HOST": "localhost", "PORT": "5432"})
    path = tmp_template("DB=${HOST}:${PORT}")
    rc = cmd.run(path)
    assert rc == 0
    captured = capsys.readouterr()
    assert captured.out == "DB=localhost:5432"


def test_cli_template_writes_output_file(tmp_template, tmp_path):
    cmd = TemplateCommand({"X": "42"})
    tpl = tmp_template("X=${X}")
    out = str(tmp_path / "out.txt")
    rc = cmd.run(tpl, output_path=out)
    assert rc == 0
    assert Path(out).read_text() == "X=42"


def test_cli_template_missing_file_returns_error(capsys):
    cmd = TemplateCommand({})
    rc = cmd.run("/nonexistent/template.txt")
    assert rc == 1
    assert "not found" in capsys.readouterr().err


def test_cli_template_strict_missing_var_returns_error(tmp_template, capsys):
    cmd = TemplateCommand({})
    path = tmp_template("value=${UNDEFINED}")
    rc = cmd.run(path, strict=True)
    assert rc == 1
    assert "UNDEFINED" in capsys.readouterr().err


def test_cli_list_placeholders(tmp_template, capsys):
    cmd = TemplateCommand({})
    path = tmp_template("${FOO} and $BAR and ${FOO}")
    rc = cmd.list_placeholders(path)
    assert rc == 0
    out = capsys.readouterr().out
    assert "FOO" in out
    assert "BAR" in out
