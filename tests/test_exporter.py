"""Tests for the EnvExporter module."""

import json
import pytest
from envchain.exporter import EnvExporter, ExportFormat


class TestEnvExporter:
    @pytest.fixture
    def exporter(self):
        return EnvExporter()

    @pytest.fixture
    def sample_vars(self):
        return {
            "DATABASE_URL": "postgres://localhost/mydb",
            "API_KEY": 'abc"def',
            "DEBUG": "true",
        }

    def test_export_bash_format(self, exporter, sample_vars):
        result = exporter.export(sample_vars, ExportFormat.BASH)
        assert 'export API_KEY="abc\\"def"' in result
        assert 'export DATABASE_URL="postgres://localhost/mydb"' in result
        assert 'export DEBUG="true"' in result

    def test_export_bash_sorted(self, exporter, sample_vars):
        result = exporter.export(sample_vars, ExportFormat.BASH)
        lines = result.strip().splitlines()
        keys = [line.split("=")[0].replace("export ", "") for line in lines]
        assert keys == sorted(keys)

    def test_export_fish_format(self, exporter, sample_vars):
        result = exporter.export(sample_vars, ExportFormat.FISH)
        assert 'set -x API_KEY "abc\\"def"' in result
        assert 'set -x DATABASE_URL "postgres://localhost/mydb"' in result

    def test_export_dotenv_format(self, exporter, sample_vars):
        result = exporter.export(sample_vars, ExportFormat.DOTENV)
        assert 'API_KEY="abc\\"def"' in result
        assert 'DATABASE_URL="postgres://localhost/mydb"' in result
        assert not result.startswith("export")

    def test_export_json_format(self, exporter, sample_vars):
        result = exporter.export(sample_vars, ExportFormat.JSON)
        parsed = json.loads(result)
        assert parsed["DATABASE_URL"] == "postgres://localhost/mydb"
        assert parsed["API_KEY"] == 'abc"def'
        assert parsed["DEBUG"] == "true"

    def test_export_empty_variables(self, exporter):
        result = exporter.export({}, ExportFormat.BASH)
        assert result == ""

    def test_export_unsupported_format_raises(self, exporter, sample_vars):
        with pytest.raises(ValueError, match="Unsupported export format"):
            exporter.export(sample_vars, "xml")  # type: ignore

    def test_export_backslash_escaping(self, exporter):
        variables = {"PATH_VAR": "C:\\Users\\test"}
        result = exporter.export(variables, ExportFormat.BASH)
        assert "C:\\\\Users\\\\test" in result

    def test_get_eval_command_bash(self, exporter):
        hint = exporter.get_eval_command(ExportFormat.BASH, "production")
        assert "envchain export production" in hint
        assert "eval" in hint

    def test_get_eval_command_fish(self, exporter):
        hint = exporter.get_eval_command(ExportFormat.FISH, "staging")
        assert "envchain export staging" in hint
        assert "source" in hint
