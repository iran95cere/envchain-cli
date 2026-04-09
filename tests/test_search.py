"""Tests for envchain.search module."""

import pytest
from unittest.mock import MagicMock
from envchain.search import EnvSearcher, SearchResult
from envchain.models import Profile


@pytest.fixture
def mock_storage():
    storage = MagicMock()
    profiles = {
        "dev": Profile(name="dev", variables={"DB_HOST": "localhost", "API_KEY": "secret123"}),
        "prod": Profile(name="prod", variables={"DB_HOST": "prod.db.example.com", "LOG_LEVEL": "error"}),
        "staging": Profile(name="staging", variables={"DEBUG": "true", "LOG_LEVEL": "debug"}),
    }
    storage.list_profiles.return_value = list(profiles.keys())
    storage.load_profile.side_effect = lambda name: profiles.get(name)
    return storage


@pytest.fixture
def searcher(mock_storage):
    return EnvSearcher(mock_storage)


def test_search_by_name_returns_matches(searcher):
    results = searcher.search("DB_HOST")
    assert len(results) == 2
    assert all(r.var_name == "DB_HOST" for r in results)
    assert all(r.matched_on == "name" for r in results)


def test_search_returns_empty_for_blank_query(searcher):
    results = searcher.search("")
    assert results == []


def test_search_case_insensitive_by_default(searcher):
    results = searcher.search("db_host")
    assert len(results) == 2


def test_search_case_sensitive(searcher):
    results = searcher.search("db_host", case_sensitive=True)
    assert len(results) == 0

    results = searcher.search("DB_HOST", case_sensitive=True)
    assert len(results) == 2


def test_search_values_enabled(searcher):
    results = searcher.search("secret", search_values=True)
    assert len(results) == 1
    assert results[0].var_name == "API_KEY"
    assert results[0].matched_on == "value"


def test_search_values_disabled_by_default(searcher):
    results = searcher.search("secret")
    assert len(results) == 0


def test_search_limited_to_specific_profiles(searcher):
    results = searcher.search("LOG_LEVEL", profile_names=["staging"])
    assert len(results) == 1
    assert results[0].profile_name == "staging"


def test_search_with_regex(searcher):
    results = searcher.search(r"^LOG", use_regex=True)
    assert len(results) == 2
    assert all(r.var_name == "LOG_LEVEL" for r in results)


def test_search_invalid_regex_raises(searcher):
    with pytest.raises(ValueError, match="Invalid regex pattern"):
        searcher.search("[invalid", use_regex=True)


def test_search_partial_name_match(searcher):
    results = searcher.search("LOG")
    assert len(results) == 2


def test_search_result_repr():
    r = SearchResult("dev", "API_KEY", "val", "name")
    assert "dev" in repr(r)
    assert "API_KEY" in repr(r)
    assert "name" in repr(r)


def test_search_nonexistent_profile_skipped(searcher, mock_storage):
    mock_storage.load_profile.side_effect = lambda name: None
    results = searcher.search("DB_HOST")
    assert results == []
