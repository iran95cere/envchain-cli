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
        assert not detector.detect("dev", {}).has_duplicates


# ---------------------------------------------------------------------------
# DuplicateDetector.detect_across
# ---------------------------------------------------------------------------

class TestDetectAcross:
    def test_returns_empty_when_no_shared_values(self, detector):
        profiles = {"dev": {"A": "1"}, "prod": {"A": "2"}}
        assert detector.detect_across(profiles) == []

    def test_detects_shared_var_value_across_profiles(self, detector):
        profiles = {"dev": {"KEY": "shared"}, "prod": {"KEY": "shared"}}
        results = detector.detect_across(profiles)
        assert len(results) == 1
        value, var_name, profile_list = results[0]
        assert var_name == "KEY"
        assert value == "shared"
        assert set(profile_list) == {"dev", "prod"}

    def test_does_not_flag_different_vars_with_same_value(self, detector):
        """Different var names with the same value across profiles are not flagged."""
        profiles = {"dev": {"A": "x"}, "prod": {"B": "x"}}
        # (A, x) only in dev, (B, x) only in prod – no cross-profile duplicate
        assert detector.detect_across(profiles) == []
