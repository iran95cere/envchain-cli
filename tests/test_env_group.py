"""Tests for envchain.env_group."""
import pytest
import os

from envchain.env_group import Group, GroupManager


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def manager(tmp_dir):
    return GroupManager(tmp_dir)


# ---------------------------------------------------------------------------
# Group dataclass
# ---------------------------------------------------------------------------

class TestGroup:
    def test_to_dict_contains_required_keys(self):
        g = Group(name="staging", profiles=["dev", "qa"], description="Staging envs")
        d = g.to_dict()
        assert d["name"] == "staging"
        assert d["profiles"] == ["dev", "qa"]
        assert d["description"] == "Staging envs"

    def test_from_dict_roundtrip(self):
        g = Group(name="prod", profiles=["live"], description="Production")
        restored = Group.from_dict(g.to_dict())
        assert restored.name == g.name
        assert restored.profiles == g.profiles
        assert restored.description == g.description

    def test_repr_contains_name(self):
        g = Group(name="alpha")
        assert "alpha" in repr(g)


# ---------------------------------------------------------------------------
# GroupManager
# ---------------------------------------------------------------------------

class TestGroupManager:
    def test_create_group(self, manager):
        g = manager.create("team-a", description="Team A profiles")
        assert g.name == "team-a"
        assert g.description == "Team A profiles"

    def test_create_duplicate_raises(self, manager):
        manager.create("dup")
        with pytest.raises(ValueError, match="already exists"):
            manager.create("dup")

    def test_list_groups_empty(self, manager):
        assert manager.list_groups() == []

    def test_list_groups_returns_created(self, manager):
        manager.create("g1")
        manager.create("g2")
        names = [g.name for g in manager.list_groups()]
        assert "g1" in names and "g2" in names

    def test_add_profile_to_group(self, manager):
        manager.create("grp")
        manager.add_profile("grp", "dev")
        g = manager.get("grp")
        assert "dev" in g.profiles

    def test_add_profile_idempotent(self, manager):
        manager.create("grp")
        manager.add_profile("grp", "dev")
        manager.add_profile("grp", "dev")
        assert manager.get("grp").profiles.count("dev") == 1

    def test_remove_profile(self, manager):
        manager.create("grp")
        manager.add_profile("grp", "dev")
        manager.remove_profile("grp", "dev")
        assert "dev" not in manager.get("grp").profiles

    def test_delete_group(self, manager):
        manager.create("temp")
        manager.delete("temp")
        assert manager.get("temp") is None

    def test_delete_missing_raises(self, manager):
        with pytest.raises(KeyError):
            manager.delete("ghost")

    def test_groups_for_profile(self, manager):
        manager.create("g1")
        manager.create("g2")
        manager.add_profile("g1", "dev")
        manager.add_profile("g2", "dev")
        result = manager.groups_for_profile("dev")
        assert set(result) == {"g1", "g2"}

    def test_persistence_across_instances(self, tmp_dir):
        m1 = GroupManager(tmp_dir)
        m1.create("persistent")
        m1.add_profile("persistent", "prod")
        m2 = GroupManager(tmp_dir)
        g = m2.get("persistent")
        assert g is not None
        assert "prod" in g.profiles
