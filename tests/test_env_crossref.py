"""Tests for env_crossref module."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from envchain.env_crossref import CrossRefEntry, CrossRefReport, EnvCrossRef


def _make_profile(vars_dict: dict) -> MagicMock:
    p = MagicMock()
    p.vars = vars_dict
    return p


def _make_storage(profiles: dict) -> MagicMock:
    s = MagicMock()
    s.list_profiles.return_value = list(profiles.keys())
    s.load_profile.side_effect = lambda name: profiles.get(name)
    return s


@pytest.fixture
def analyser():
    storage = _make_storage({
        "dev": _make_profile({"DB_URL": "dev_db", "API_KEY": "abc"}),
        "prod": _make_profile({"DB_URL": "prod_db", "SECRET": "xyz"}),
        "staging": _make_profile({"DB_URL": "stg_db", "API_KEY": "def"}),
    })
    return EnvCrossRef(storage)


class TestCrossRefEntry:
    def test_to_dict_contains_required_keys(self):
        e = CrossRefEntry(name="DB_URL", profiles=["dev", "prod"])
        d = e.to_dict()
        assert "name" in d and "profiles" in d

    def test_from_dict_roundtrip(self):
        e = CrossRefEntry(name="API_KEY", profiles=["dev", "staging"])
        assert CrossRefEntry.from_dict(e.to_dict()).name == "API_KEY"

    def test_from_dict_missing_profiles_defaults_empty(self):
        e = CrossRefEntry.from_dict({"name": "X"})
        assert e.profiles == []

    def test_profile_count(self):
        e = CrossRefEntry(name="X", profiles=["a", "b", "c"])
        assert e.profile_count() == 3

    def test_repr_contains_name(self):
        e = CrossRefEntry(name="MY_VAR", profiles=["dev"])
        assert "MY_VAR" in repr(e)


class TestCrossRefReport:
    def test_ref_count_zero_when_empty(self):
        r = CrossRefReport()
        assert r.ref_count == 0

    def test_has_refs_false_when_empty(self):
        assert not CrossRefReport().has_refs

    def test_has_refs_true_when_entries_present(self):
        r = CrossRefReport(entries=[CrossRefEntry("X", ["a", "b"])])
        assert r.has_refs

    def test_names_returns_entry_names(self):
        r = CrossRefReport(entries=[
            CrossRefEntry("A", ["x", "y"]),
            CrossRefEntry("B", ["x", "z"]),
        ])
        assert r.names() == ["A", "B"]


class TestEnvCrossRef:
    def test_shared_vars_detected(self, analyser):
        report = analyser.analyse()
        names = report.names()
        assert "DB_URL" in names
        assert "API_KEY" in names

    def test_unique_var_not_in_report(self, analyser):
        report = analyser.analyse()
        assert "SECRET" not in report.names()

    def test_analyse_subset_of_profiles(self, analyser):
        report = analyser.analyse(["dev", "prod"])
        names = report.names()
        assert "DB_URL" in names
        assert "API_KEY" not in names

    def test_missing_profile_skipped(self):
        storage = _make_storage({"dev": _make_profile({"X": "1"}), "ghost": None})
        a = EnvCrossRef(storage)
        report = a.analyse()
        assert report.ref_count == 0
