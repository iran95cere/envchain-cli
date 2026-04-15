"""Tests for envchain.env_duplicates."""
import pytest

from envchain.env_duplicates import (
    DuplicateDetector,
    DuplicateGroup,
    DuplicateReport,
)


@pytest.fixture
def detector() -> DuplicateDetector:
    return DuplicateDetector()


# ---------------------------------------------------------------------------
# DuplicateGroup
# ---------------------------------------------------------------------------

class TestDuplicateGroup:
    def test_to_dict_contains_required_keys(self):
        g = DuplicateGroup(value="secret", names=["A", "B"])
        d = g.to_dict()
        assert "value" in d
        assert "names" in d

    def test_from_dict_roundtrip(self):
        g = DuplicateGroup(value="x", names=["FOO", "BAR"])
        assert DuplicateGroup.from_dict(g.to_dict()).names == ["FOO", "BAR"]

    def test_from_dict_missing_names_defaults_empty(self):
        g = DuplicateGroup.from_dict({"value": "v"})
        assert g.names == []

    def test_from_dict_missing_value_defaults_empty_string(self):
        g = DuplicateGroup.from_dict({"names": ["A", "B"]})
        assert g.value == ""


# ---------------------------------------------------------------------------
# DuplicateReport
# ---------------------------------------------------------------------------

class TestDuplicateReport:
    def test_has_duplicates_false_when_empty(self):
        r = DuplicateReport(profile="dev")
        assert not r.has_duplicates

    def test_has_duplicates_true_when_groups_present(self):
        r = DuplicateReport(
            profile="dev",
            groups=[DuplicateGroup(value="x", names=["A", "B"])],
        )
        assert r.has_duplicates

    def test_duplicate_count_sums_names(self):
        r = DuplicateReport(
            profile="dev",
            groups=[
                DuplicateGroup(value="x", names=["A", "B"]),
                DuplicateGroup(value="y", names=["C", "D", "E"]),
            ],
        )
        assert r.duplicate_count == 5

    def test_duplicate_count_zero_when_no_groups(self):
        assert DuplicateReport(profile="dev").duplicate_count == 0


# ---------------------------------------------------------------------------
# DuplicateDetector.detect
# ---------------------------------------------------------------------------

class TestDetect:
    def test_no_duplicates_returns_empty_report(self, detector):
        report = detector.detect("dev", {"A": "1", "B": "2", "C": "3"})
        assert not report.has_duplicates
        assert report.profile == "dev"

    def test_detects_two_vars_with_same_value(self, detector):
        report = detector.detect("dev", {"A": "same", "B": "same", "C": "other"})
        assert report.has_duplicates
        assert len(report.groups) == 1
        assert sorted(report.groups[0].names) == ["A", "B"]

    def test_groups_sorted_by_first_name(self, detector):
        report = detector.detect(
            "dev",
            {"X": "val2", "Y": "val2", "A": "val1", "B": "val1"},
        )
        assert report.groups[0].names[0] == "A"
        assert report.groups[1].names[0] == "X"

    def test_empty_variables_returns_no_duplicates(self, detector):
        report = detector.detect("dev", {})
        assert not report.has_duplicates
        assert report.duplicate_count == 0

    def test_single_variable_returns_no_duplicates(self, detector):
        report = detector.detect("dev", {"ONLY": "value"})
        assert not report.has_duplicates

    def test_multiple_groups_detected(self, detector):
        report = detector.detect(
            "prod",
            {"A": "v1", "B": "v1", "C": "v2", "D": "v2"},
        )
        assert len(report.groups) == 2
        assert report.duplicate_count == 4
