"""Tests for envchain.env_rename."""
import pytest

from envchain.env_rename import EnvRenamer, RenameResult


@pytest.fixture
def renamer() -> EnvRenamer:
    return EnvRenamer()


@pytest.fixture
def sample_vars() -> dict:
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "secret"}


class TestRenameResult:
    def test_success_count(self):
        r = RenameResult(renamed={"A": "B", "C": "D"})
        assert r.success_count == 2

    def test_has_issues_false_when_clean(self):
        r = RenameResult(renamed={"A": "B"})
        assert not r.has_issues

    def test_has_issues_true_when_skipped(self):
        r = RenameResult(skipped=["MISSING"])
        assert r.has_issues

    def test_has_issues_true_when_conflict(self):
        r = RenameResult(conflicts=["OLD"])
        assert r.has_issues


class TestEnvRenamer:
    def test_rename_single_key(self, renamer, sample_vars):
        result = renamer.rename(sample_vars, {"DB_HOST": "DATABASE_HOST"})
        assert "DATABASE_HOST" in sample_vars
        assert "DB_HOST" not in sample_vars
        assert result.renamed == {"DB_HOST": "DATABASE_HOST"}

    def test_rename_missing_key_is_skipped(self, renamer, sample_vars):
        result = renamer.rename(sample_vars, {"MISSING": "NEW_NAME"})
        assert "MISSING" in result.skipped
        assert result.success_count == 0

    def test_rename_conflict_without_overwrite(self, renamer, sample_vars):
        # Rename DB_HOST onto existing DB_PORT
        result = renamer.rename(sample_vars, {"DB_HOST": "DB_PORT"})
        assert "DB_HOST" in result.conflicts
        assert "DB_HOST" in sample_vars  # unchanged

    def test_rename_conflict_with_overwrite(self, renamer, sample_vars):
        result = renamer.rename(sample_vars, {"DB_HOST": "DB_PORT"}, overwrite=True)
        assert result.renamed == {"DB_HOST": "DB_PORT"}
        assert sample_vars["DB_PORT"] == "localhost"  # value from DB_HOST

    def test_rename_same_name_is_noop(self, renamer, sample_vars):
        original = dict(sample_vars)
        result = renamer.rename(sample_vars, {"DB_HOST": "DB_HOST"})
        assert result.renamed == {"DB_HOST": "DB_HOST"}
        assert sample_vars == original

    def test_batch_rename(self, renamer, sample_vars):
        mapping = {"DB_HOST": "DATABASE_HOST", "API_KEY": "API_SECRET"}
        result = renamer.rename(sample_vars, mapping)
        assert result.success_count == 2
        assert "DATABASE_HOST" in sample_vars
        assert "API_SECRET" in sample_vars

    def test_rename_one_returns_value(self, renamer, sample_vars):
        val = renamer.rename_one(sample_vars, "DB_PORT", "DATABASE_PORT")
        assert val == "5432"
        assert "DATABASE_PORT" in sample_vars

    def test_rename_one_returns_none_on_missing(self, renamer, sample_vars):
        val = renamer.rename_one(sample_vars, "NOPE", "SOMETHING")
        assert val is None

    def test_rename_one_returns_none_on_conflict(self, renamer, sample_vars):
        # DB_PORT already exists, so renaming DB_HOST -> DB_PORT should return None
        val = renamer.rename_one(sample_vars, "DB_HOST", "DB_PORT")
        assert val is None
        assert "DB_HOST" in sample_vars  # original key should remain untouched
