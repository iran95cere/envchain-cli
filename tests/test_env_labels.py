"""Tests for envchain.env_labels."""
import pytest
from envchain.env_labels import LabelEntry, LabelManager


@pytest.fixture
def mgr():
    return LabelManager()


class TestLabelEntry:
    def test_to_dict_contains_required_keys(self):
        e = LabelEntry(var_name="DB_URL", label="database", description="Primary DB")
        d = e.to_dict()
        assert d["var_name"] == "DB_URL"
        assert d["label"] == "database"
        assert d["description"] == "Primary DB"

    def test_from_dict_roundtrip(self):
        e = LabelEntry(var_name="API_KEY", label="secret", description="")
        assert LabelEntry.from_dict(e.to_dict()) == e

    def test_from_dict_missing_description_defaults_empty(self):
        e = LabelEntry.from_dict({"var_name": "X", "label": "misc"})
        assert e.description == ""

    def test_repr_contains_var_and_label(self):
        e = LabelEntry(var_name="PORT", label="network")
        r = repr(e)
        assert "PORT" in r
        assert "network" in r


class TestLabelManager:
    def test_add_and_get(self, mgr):
        mgr.add("DB_URL", "database")
        e = mgr.get("DB_URL")
        assert e is not None
        assert e.label == "database"

    def test_add_empty_var_raises(self, mgr):
        with pytest.raises(ValueError):
            mgr.add("", "label")

    def test_add_empty_label_raises(self, mgr):
        with pytest.raises(ValueError):
            mgr.add("VAR", "")

    def test_remove_existing_returns_true(self, mgr):
        mgr.add("X", "misc")
        assert mgr.remove("X") is True
        assert mgr.get("X") is None

    def test_remove_missing_returns_false(self, mgr):
        assert mgr.remove("NONEXISTENT") is False

    def test_all_entries_empty(self, mgr):
        assert mgr.all_entries() == []

    def test_all_entries_returns_all(self, mgr):
        mgr.add("A", "alpha")
        mgr.add("B", "beta")
        names = {e.var_name for e in mgr.all_entries()}
        assert names == {"A", "B"}

    def test_labeled_vars_case_insensitive(self, mgr):
        mgr.add("DB_HOST", "Database")
        mgr.add("DB_PORT", "database")
        mgr.add("API_KEY", "secret")
        result = mgr.labeled_vars("DATABASE")
        assert set(result) == {"DB_HOST", "DB_PORT"}

    def test_labeled_vars_no_match(self, mgr):
        mgr.add("X", "misc")
        assert mgr.labeled_vars("unknown") == []

    def test_to_dict_and_from_dict_roundtrip(self, mgr):
        mgr.add("URL", "endpoint", "Service URL")
        mgr.add("KEY", "secret")
        restored = LabelManager.from_dict(mgr.to_dict())
        assert restored.get("URL").label == "endpoint"
        assert restored.get("KEY").description == ""

    def test_overwrite_existing_label(self, mgr):
        mgr.add("VAR", "old")
        mgr.add("VAR", "new")
        assert mgr.get("VAR").label == "new"
