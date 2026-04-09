"""Tests for envchain.tags module."""
import pytest
from envchain.tags import TagIndex


@pytest.fixture
def index() -> TagIndex:
    return TagIndex()


class TestTagIndex:
    def test_add_and_profiles_for_tag(self, index: TagIndex) -> None:
        index.add("production", "prod-api")
        index.add("production", "prod-db")
        assert index.profiles_for_tag("production") == ["prod-api", "prod-db"]

    def test_add_normalises_tag_case(self, index: TagIndex) -> None:
        index.add("  Production  ", "prod-api")
        assert "production" in index.all_tags()

    def test_add_empty_tag_raises(self, index: TagIndex) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            index.add("", "some-profile")

    def test_add_whitespace_only_tag_raises(self, index: TagIndex) -> None:
        with pytest.raises(ValueError):
            index.add("   ", "some-profile")

    def test_remove_tag_from_profile(self, index: TagIndex) -> None:
        index.add("staging", "staging-api")
        index.remove("staging", "staging-api")
        assert index.profiles_for_tag("staging") == []

    def test_remove_cleans_up_empty_tag(self, index: TagIndex) -> None:
        index.add("temp", "p1")
        index.remove("temp", "p1")
        assert "temp" not in index.all_tags()

    def test_remove_nonexistent_tag_is_safe(self, index: TagIndex) -> None:
        index.remove("ghost", "p1")  # should not raise

    def test_tags_for_profile(self, index: TagIndex) -> None:
        index.add("web", "api")
        index.add("production", "api")
        assert index.tags_for_profile("api") == ["production", "web"]

    def test_tags_for_profile_with_no_tags(self, index: TagIndex) -> None:
        assert index.tags_for_profile("unknown") == []

    def test_all_tags_sorted(self, index: TagIndex) -> None:
        index.add("zebra", "p1")
        index.add("alpha", "p2")
        assert index.all_tags() == ["alpha", "zebra"]

    def test_to_dict_roundtrip(self, index: TagIndex) -> None:
        index.add("production", "api")
        index.add("production", "db")
        index.add("internal", "db")
        data = index.to_dict()
        restored = TagIndex.from_dict(data)
        assert restored.profiles_for_tag("production") == ["api", "db"]
        assert restored.tags_for_profile("db") == ["internal", "production"]

    def test_from_dict_empty(self) -> None:
        idx = TagIndex.from_dict({})
        assert idx.all_tags() == []

    def test_duplicate_add_does_not_duplicate_profile(self, index: TagIndex) -> None:
        index.add("ci", "pipeline")
        index.add("ci", "pipeline")
        assert index.profiles_for_tag("ci") == ["pipeline"]
