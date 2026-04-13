"""Tests for envchain.env_preset."""
import pytest

from envchain.env_preset import Preset, PresetManager


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def manager(tmp_dir):
    return PresetManager(tmp_dir)


class TestPreset:
    def test_to_dict_contains_required_keys(self):
        p = Preset(name="base", description="Base preset", vars={"FOO": "bar"})
        d = p.to_dict()
        assert "name" in d
        assert "description" in d
        assert "vars" in d

    def test_from_dict_roundtrip(self):
        p = Preset(name="base", description="desc", vars={"A": "1"})
        p2 = Preset.from_dict(p.to_dict())
        assert p2.name == p.name
        assert p2.description == p.description
        assert p2.vars == p.vars

    def test_from_dict_missing_description_defaults_empty(self):
        p = Preset.from_dict({"name": "x", "vars": {}})
        assert p.description == ""

    def test_repr_contains_name(self):
        p = Preset(name="mypre", description="", vars={"K": "V"})
        assert "mypre" in repr(p)


class TestPresetManager:
    def test_add_and_get(self, manager):
        manager.add("dev", "Dev defaults", {"DEBUG": "true"})
        p = manager.get("dev")
        assert p is not None
        assert p.vars["DEBUG"] == "true"

    def test_add_empty_name_raises(self, manager):
        with pytest.raises(ValueError):
            manager.add("", "", {})

    def test_remove_existing(self, manager):
        manager.add("tmp", "", {"X": "1"})
        assert manager.remove("tmp") is True
        assert manager.get("tmp") is None

    def test_remove_nonexistent_returns_false(self, manager):
        assert manager.remove("ghost") is False

    def test_list_presets_sorted(self, manager):
        manager.add("z_preset", "", {})
        manager.add("a_preset", "", {})
        names = [p.name for p in manager.list_presets()]
        assert names == sorted(names)

    def test_apply_fills_missing_vars(self, manager):
        manager.add("base", "", {"FOO": "foo", "BAR": "bar"})
        result = manager.apply("base", {"FOO": "existing"})
        assert result["FOO"] == "existing"  # not overwritten
        assert result["BAR"] == "bar"

    def test_apply_overwrite_replaces_existing(self, manager):
        manager.add("base", "", {"FOO": "preset_val"})
        result = manager.apply("base", {"FOO": "old"}, overwrite=True)
        assert result["FOO"] == "preset_val"

    def test_apply_unknown_preset_raises(self, manager):
        with pytest.raises(KeyError):
            manager.apply("no_such", {})

    def test_persistence_across_instances(self, tmp_dir):
        m1 = PresetManager(tmp_dir)
        m1.add("persist", "desc", {"K": "V"})
        m2 = PresetManager(tmp_dir)
        assert m2.get("persist") is not None
