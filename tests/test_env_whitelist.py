"""Tests for envchain.env_whitelist."""

import os
import pytest

from envchain.env_whitelist import (
    WhitelistManager,
    WhitelistReport,
    WhitelistViolation,
)


@pytest.fixture()
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture()
def manager(tmp_dir):
    return WhitelistManager(tmp_dir)


# ---------------------------------------------------------------------------
# WhitelistViolation
# ---------------------------------------------------------------------------

class TestWhitelistViolation:
    def test_repr_contains_var_and_profile(self):
        v = WhitelistViolation(var_name="SECRET", profile="prod")
        assert "SECRET" in repr(v)
        assert "prod" in repr(v)


# ---------------------------------------------------------------------------
# WhitelistReport
# ---------------------------------------------------------------------------

class TestWhitelistReport:
    def test_has_violations_false_when_empty(self):
        r = WhitelistReport(checked=3)
        assert not r.has_violations

    def test_has_violations_true_when_present(self):
        r = WhitelistReport(
            violations=[WhitelistViolation("X", "dev")], checked=1
        )
        assert r.has_violations

    def test_violation_count(self):
        r = WhitelistReport(
            violations=[WhitelistViolation("A", "p"), WhitelistViolation("B", "p")]
        )
        assert r.violation_count == 2

    def test_repr_contains_counts(self):
        r = WhitelistReport(checked=5)
        assert "5" in repr(r)


# ---------------------------------------------------------------------------
# WhitelistManager
# ---------------------------------------------------------------------------

class TestWhitelistManager:
    def test_get_empty_when_no_entries(self, manager):
        assert manager.get("dev") == []

    def test_add_and_get(self, manager):
        manager.add("dev", "DB_URL")
        assert "DB_URL" in manager.get("dev")

    def test_add_duplicate_is_idempotent(self, manager):
        manager.add("dev", "DB_URL")
        manager.add("dev", "DB_URL")
        assert manager.get("dev").count("DB_URL") == 1

    def test_add_empty_name_raises(self, manager):
        with pytest.raises(ValueError):
            manager.add("dev", "")

    def test_remove_existing_returns_true(self, manager):
        manager.add("dev", "API_KEY")
        assert manager.remove("dev", "API_KEY") is True
        assert "API_KEY" not in manager.get("dev")

    def test_remove_missing_returns_false(self, manager):
        assert manager.remove("dev", "NONEXISTENT") is False

    def test_is_enabled_false_when_empty(self, manager):
        assert not manager.is_enabled("prod")

    def test_is_enabled_true_after_add(self, manager):
        manager.add("prod", "PORT")
        assert manager.is_enabled("prod")

    def test_check_no_violations_when_disabled(self, manager):
        report = manager.check("dev", {"ANY_VAR": "value"})
        assert not report.has_violations

    def test_check_passes_allowed_vars(self, manager):
        manager.add("dev", "DB_URL")
        manager.add("dev", "PORT")
        report = manager.check("dev", {"DB_URL": "x", "PORT": "5432"})
        assert not report.has_violations

    def test_check_flags_disallowed_var(self, manager):
        manager.add("dev", "DB_URL")
        report = manager.check("dev", {"DB_URL": "x", "SECRET": "y"})
        assert report.has_violations
        assert report.violations[0].var_name == "SECRET"

    def test_check_report_checked_count(self, manager):
        manager.add("dev", "A")
        report = manager.check("dev", {"A": "1", "B": "2", "C": "3"})
        assert report.checked == 3

    def test_persists_across_instances(self, tmp_dir):
        m1 = WhitelistManager(tmp_dir)
        m1.add("ci", "CI_TOKEN")
        m2 = WhitelistManager(tmp_dir)
        assert "CI_TOKEN" in m2.get("ci")
