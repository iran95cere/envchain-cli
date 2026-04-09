"""Tests for EnvImporter."""

import json
import pytest
from pathlib import Path

from envchain.importer import EnvImporter, ImportFormat


@pytest.fixture
def importer():
    return EnvImporter()


@pytest.fixture
def tmp_file(tmp_path):
    def _write(name, content):
        p = tmp_path / name
        p.write_text(content, encoding="utf-8")
        return str(p)
    return _write


class TestEnvImporter:
    def test_parse_dotenv_basic(self, importer, tmp_file):
        path = tmp_file(".env", "FOO=bar\nBAZ=qux\n")
        result = importer.import_file(path)
        assert result == {"FOO": "bar", "BAZ": "qux"}

    def test_parse_dotenv_ignores_comments(self, importer, tmp_file):
        path = tmp_file(".env", "# comment\nKEY=value\n")
        result = importer.import_file(path)
        assert "KEY" in result
        assert len(result) == 1

    def test_parse_dotenv_quoted_values(self, importer, tmp_file):
        path = tmp_file(".env", 'SECRET="my secret"\nTOKEN=\'abc123\'\n')
        result = importer.import_file(path)
        assert result["SECRET"] == "my secret"
        assert result["TOKEN"] == "abc123"

    def test_parse_shell_export_statements(self, importer, tmp_file):
        path = tmp_file("env.sh", 'export DB_HOST="localhost"\nexport PORT=5432\n')
        result = importer.import_file(path)
        assert result["DB_HOST"] == "localhost"
        assert result["PORT"] == "5432"

    def test_parse_json_format(self, importer, tmp_file):
        data = {"API_KEY": "abc", "REGION": "us-east-1"}
        path = tmp_file("vars.json", json.dumps(data))
        result = importer.import_file(path)
        assert result == data

    def test_auto_detect_json_by_extension(self, importer, tmp_file):
        data = {"X": "1"}
        path = tmp_file("config.json", json.dumps(data))
        result = importer.import_file(path)
        assert result["X"] == "1"

    def test_auto_detect_shell_by_extension(self, importer, tmp_file):
        path = tmp_file("setup.sh", "export SHELL_VAR=hello\n")
        result = importer.import_file(path)
        assert result["SHELL_VAR"] == "hello"

    def test_explicit_format_override(self, importer, tmp_file):
        # File named .sh but parsed as dotenv
        path = tmp_file("weird.sh", "KEY=value\n")
        result = importer.import_file(path, fmt=ImportFormat.DOTENV)
        assert result["KEY"] == "value"

    def test_file_not_found_raises(self, importer):
        with pytest.raises(FileNotFoundError):
            importer.import_file("/nonexistent/path/.env")

    def test_json_non_dict_raises(self, importer, tmp_file):
        path = tmp_file("bad.json", '["not", "a", "dict"]')
        with pytest.raises(ValueError, match="top-level object"):
            importer.import_file(path, fmt=ImportFormat.JSON)
