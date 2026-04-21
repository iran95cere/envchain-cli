"""Tests for env_annotate module."""
import pytest
import os
from envchain.env_annotate import Annotation, AnnotationManager


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def manager(tmp_dir):
    return AnnotationManager(tmp_dir, "dev")


class TestAnnotation:
    def test_to_dict_contains_required_keys(self):
        ann = Annotation(var_name="DB_URL", note="Primary database", author="alice")
        d = ann.to_dict()
        assert "var_name" in d
        assert "note" in d
        assert "author" in d
        assert "created_at" in d

    def test_from_dict_roundtrip(self):
        ann = Annotation(var_name="API_KEY", note="Third-party key", author="bob")
        restored = Annotation.from_dict(ann.to_dict())
        assert restored.var_name == ann.var_name
        assert restored.note == ann.note
        assert restored.author == ann.author
        assert restored.created_at == ann.created_at

    def test_from_dict_missing_author_defaults_empty(self):
        d = {"var_name": "X", "note": "some note", "created_at": "2024-01-01T00:00:00+00:00"}
        ann = Annotation.from_dict(d)
        assert ann.author == ""

    def test_repr_contains_var_and_note(self):
        ann = Annotation(var_name="TOKEN", note="Auth token")
        r = repr(ann)
        assert "TOKEN" in r
        assert "Auth token" in r


class TestAnnotationManager:
    def test_add_and_get(self, manager):
        manager.add("DB_HOST", "Hostname for DB", author="dev")
        ann = manager.get("DB_HOST")
        assert ann is not None
        assert ann.note == "Hostname for DB"
        assert ann.author == "dev"

    def test_get_missing_returns_none(self, manager):
        assert manager.get("MISSING") is None

    def test_remove_existing(self, manager):
        manager.add("KEY", "some note")
        result = manager.remove("KEY")
        assert result is True
        assert manager.get("KEY") is None

    def test_remove_missing_returns_false(self, manager):
        assert manager.remove("NONEXISTENT") is False

    def test_all_returns_all_annotations(self, manager):
        manager.add("A", "note a")
        manager.add("B", "note b")
        all_anns = manager.all()
        names = {a.var_name for a in all_anns}
        assert names == {"A", "B"}

    def test_persistence_across_instances(self, tmp_dir):
        m1 = AnnotationManager(tmp_dir, "staging")
        m1.add("SECRET", "very secret", author="ops")
        m2 = AnnotationManager(tmp_dir, "staging")
        ann = m2.get("SECRET")
        assert ann is not None
        assert ann.note == "very secret"

    def test_overwrite_existing(self, manager):
        manager.add("KEY", "old note")
        manager.add("KEY", "new note")
        assert manager.get("KEY").note == "new note"
        assert len(manager.all()) == 1
