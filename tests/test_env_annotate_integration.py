"""Integration tests for annotation persistence with real file I/O."""
import pytest
import os
from envchain.env_annotate import AnnotationManager


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


class TestAnnotationIntegration:
    def test_annotation_file_created_on_add(self, tmp_dir):
        m = AnnotationManager(tmp_dir, "prod")
        m.add("API_KEY", "Production API key")
        expected = os.path.join(tmp_dir, "prod.annotations.json")
        assert os.path.exists(expected)

    def test_no_file_created_when_no_annotations(self, tmp_dir):
        AnnotationManager(tmp_dir, "empty")
        expected = os.path.join(tmp_dir, "empty.annotations.json")
        assert not os.path.exists(expected)

    def test_multiple_profiles_isolated(self, tmp_dir):
        m_dev = AnnotationManager(tmp_dir, "dev")
        m_prod = AnnotationManager(tmp_dir, "prod")
        m_dev.add("KEY", "dev note")
        m_prod.add("KEY", "prod note")
        assert m_dev.get("KEY").note == "dev note"
        assert m_prod.get("KEY").note == "prod note"

    def test_remove_then_reload_is_gone(self, tmp_dir):
        m1 = AnnotationManager(tmp_dir, "staging")
        m1.add("SECRET", "to be removed")
        m1.remove("SECRET")
        m2 = AnnotationManager(tmp_dir, "staging")
        assert m2.get("SECRET") is None

    def test_update_persists_new_note(self, tmp_dir):
        m1 = AnnotationManager(tmp_dir, "dev")
        m1.add("DB_URL", "old note")
        m1.add("DB_URL", "updated note")
        m2 = AnnotationManager(tmp_dir, "dev")
        ann = m2.get("DB_URL")
        assert ann.note == "updated note"
