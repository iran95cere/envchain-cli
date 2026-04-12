"""Tests for envchain.cli_deprecation."""
import json
import pytest
from pathlib import Path
from envchain.cli_deprecation import DeprecationCommand


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


@pytest.fixture
def cmd(tmp_dir):
    return DeprecationCommand(storage_dir=str(tmp_dir))


class TestDeprecationCommand:
    def test_add_registers_entry(self, cmd, tmp_dir):
        cmd.add("OLD_KEY", reason="renamed", replacement="NEW_KEY")
        registry_file = tmp_dir / ".envchain_deprecations.json"
        assert registry_file.exists()
        data = json.loads(registry_file.read_text())
        names = [e["var_name"] for e in data["entries"]]
        assert "OLD_KEY" in names

    def test_add_prints_confirmation(self, cmd, capsys):
        cmd.add("OLD_VAR", reason="unused")
        out = capsys.readouterr().out
        assert "OLD_VAR" in out

    def test_add_with_replacement_mentions_it(self, cmd, capsys):
        cmd.add("OLD_VAR", reason="renamed", replacement="NEW_VAR")
        out = capsys.readouterr().out
        assert "NEW_VAR" in out

    def test_remove_existing_entry(self, cmd, capsys):
        cmd.add("OLD_KEY", reason="r")
        cmd.remove("OLD_KEY")
        out = capsys.readouterr().out
        assert "Removed" in out

    def test_remove_missing_entry_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.remove("NONEXISTENT")

    def test_list_deprecated_empty(self, cmd, capsys):
        cmd.list_deprecated()
        out = capsys.readouterr().out
        assert "No deprecated" in out

    def test_list_deprecated_shows_entries(self, cmd, capsys):
        cmd.add("OLD_A", reason="gone")
        cmd.add("OLD_B", reason="renamed", replacement="NEW_B")
        cmd.list_deprecated()
        out = capsys.readouterr().out
        assert "OLD_A" in out
        assert "OLD_B" in out

    def test_scan_no_matches_prints_clean(self, cmd, capsys):
        cmd.add("OLD_KEY", reason="renamed")
        cmd.scan({"FRESH_KEY": "value"})
        out = capsys.readouterr().out
        assert "No deprecated" in out

    def test_scan_flags_deprecated_vars(self, cmd, capsys):
        cmd.add("OLD_KEY", reason="renamed", replacement="NEW_KEY")
        cmd.scan({"OLD_KEY": "secret"})
        out = capsys.readouterr().out
        assert "WARNING" in out
        assert "OLD_KEY" in out

    def test_persistence_across_instances(self, tmp_dir):
        c1 = DeprecationCommand(storage_dir=str(tmp_dir))
        c1.add("PERSIST_KEY", reason="test")
        c2 = DeprecationCommand(storage_dir=str(tmp_dir))
        entries = c2._checker.all_deprecated()
        assert any(e.var_name == "PERSIST_KEY" for e in entries)
