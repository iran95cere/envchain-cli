"""Tests for envchain.env_namespace."""

import pytest

from envchain.env_namespace import EnvNamespace, NamespaceGroup, NamespaceReport


@pytest.fixture()
def ns() -> EnvNamespace:
    return EnvNamespace(separator="_")


# ---------------------------------------------------------------------------
# NamespaceGroup
# ---------------------------------------------------------------------------

class TestNamespaceGroup:
    def test_to_dict_contains_required_keys(self):
        g = NamespaceGroup(prefix="DB", vars={"DB_HOST": "localhost"})
        d = g.to_dict()
        assert "prefix" in d
        assert "vars" in d

    def test_from_dict_roundtrip(self):
        g = NamespaceGroup(prefix="AWS", vars={"AWS_KEY": "abc", "AWS_SECRET": "xyz"})
        restored = NamespaceGroup.from_dict(g.to_dict())
        assert restored.prefix == g.prefix
        assert restored.vars == g.vars

    def test_from_dict_missing_vars_defaults_empty(self):
        g = NamespaceGroup.from_dict({"prefix": "X"})
        assert g.vars == {}


# ---------------------------------------------------------------------------
# NamespaceReport
# ---------------------------------------------------------------------------

class TestNamespaceReport:
    def test_group_count(self):
        r = NamespaceReport(
            groups={"DB": NamespaceGroup("DB"), "AWS": NamespaceGroup("AWS")}
        )
        assert r.group_count == 2

    def test_ungrouped_count(self):
        r = NamespaceReport(ungrouped={"PLAIN": "val"})
        assert r.ungrouped_count == 1


# ---------------------------------------------------------------------------
# EnvNamespace.partition with explicit prefixes
# ---------------------------------------------------------------------------

class TestEnvNamespacePartition:
    def test_groups_by_explicit_prefix(self, ns):
        vars = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_NAME": "myapp"}
        report = ns.partition(vars, prefixes=["DB"])
        assert "DB" in report.groups
        assert set(report.groups["DB"].vars) == {"DB_HOST", "DB_PORT"}
        assert "APP_NAME" in report.ungrouped

    def test_ungrouped_when_no_match(self, ns):
        vars = {"PLAIN": "value", "OTHER": "stuff"}
        report = ns.partition(vars, prefixes=["DB"])
        assert report.group_count == 0
        assert set(report.ungrouped) == {"PLAIN", "OTHER"}

    def test_exact_prefix_name_included(self, ns):
        vars = {"DB": "main", "DB_HOST": "localhost"}
        report = ns.partition(vars, prefixes=["DB"])
        assert "DB" in report.groups["DB"].vars
        assert "DB_HOST" in report.groups["DB"].vars

    def test_empty_vars_returns_empty_report(self, ns):
        report = ns.partition({}, prefixes=["DB"])
        assert report.group_count == 0
        assert report.ungrouped_count == 0


# ---------------------------------------------------------------------------
# EnvNamespace.partition with auto-discovery
# ---------------------------------------------------------------------------

class TestEnvNamespaceAutoDiscover:
    def test_discovers_repeated_prefix(self, ns):
        vars = {
            "DB_HOST": "h",
            "DB_PORT": "5432",
            "AWS_KEY": "k",
            "AWS_SECRET": "s",
            "STANDALONE": "x",
        }
        report = ns.partition(vars)
        assert "DB" in report.groups
        assert "AWS" in report.groups
        assert "STANDALONE" in report.ungrouped

    def test_single_occurrence_prefix_not_grouped(self, ns):
        vars = {"DB_HOST": "h", "UNIQUE_KEY": "val"}
        report = ns.partition(vars)
        # UNIQUE appears only once — should NOT form a group
        assert "UNIQUE" not in report.groups


# ---------------------------------------------------------------------------
# Constructor validation
# ---------------------------------------------------------------------------

def test_empty_separator_raises():
    with pytest.raises(ValueError, match="separator"):
        EnvNamespace(separator="")
