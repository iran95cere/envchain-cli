"""Tests for envchain.env_dependencies."""
import pytest

from envchain.env_dependencies import (
    DependencyAnalyser,
    DependencyEdge,
    DependencyReport,
)


@pytest.fixture
def analyser() -> DependencyAnalyser:
    return DependencyAnalyser()


PROFILES = {
    "base": {"DB_HOST": "localhost", "DB_PORT": "5432"},
    "app": {
        "DATABASE_URL": "postgres://${base:DB_HOST}:${base:DB_PORT}/mydb",
        "SECRET": "plain-value",
    },
    "staging": {
        "API_KEY": "${app:SECRET}",
        "MISSING_REF": "${ghost:NOPE}",
    },
}


class TestDependencyEdge:
    def test_to_dict_contains_required_keys(self):
        edge = DependencyEdge("A", "B", "p1", "p2")
        d = edge.to_dict()
        assert "source_var" in d
        assert "target_var" in d
        assert "source_profile" in d
        assert "target_profile" in d

    def test_from_dict_roundtrip(self):
        edge = DependencyEdge("A", "B", "p1", "p2")
        assert DependencyEdge.from_dict(edge.to_dict()) == edge

    def test_repr_contains_profiles(self):
        edge = DependencyEdge("X", "Y", "src", "dst")
        r = repr(edge)
        assert "src" in r
        assert "dst" in r


class TestDependencyReport:
    def test_edge_count_zero_when_empty(self):
        report = DependencyReport()
        assert report.edge_count == 0

    def test_has_missing_false_when_empty(self):
        report = DependencyReport()
        assert not report.has_missing

    def test_has_missing_true_when_present(self):
        edge = DependencyEdge("A", "B", "p1", "p2")
        report = DependencyReport(missing=[edge])
        assert report.has_missing

    def test_repr_contains_counts(self):
        report = DependencyReport()
        assert "edges=0" in repr(report)


class TestDependencyAnalyser:
    def test_no_refs_returns_empty_report(self, analyser):
        report = analyser.analyse(PROFILES, "base")
        assert report.edge_count == 0
        assert not report.has_missing

    def test_detects_cross_profile_refs(self, analyser):
        report = analyser.analyse(PROFILES, "app")
        assert report.edge_count == 2

    def test_all_refs_resolved_when_target_exists(self, analyser):
        report = analyser.analyse(PROFILES, "app")
        assert not report.has_missing

    def test_detects_missing_ref(self, analyser):
        report = analyser.analyse(PROFILES, "staging")
        assert report.has_missing
        assert len(report.missing) == 1
        assert report.missing[0].target_profile == "ghost"

    def test_unknown_source_profile_returns_empty(self, analyser):
        report = analyser.analyse(PROFILES, "nonexistent")
        assert report.edge_count == 0

    def test_extract_refs_multiple_in_one_value(self, analyser):
        refs = analyser._extract_refs("${p1:A} and ${p2:B}")
        assert len(refs) == 2
        assert ("p1", "A") in refs
        assert ("p2", "B") in refs

    def test_extract_refs_ignores_non_cross_profile(self, analyser):
        refs = analyser._extract_refs("plain value without refs")
        assert refs == []
