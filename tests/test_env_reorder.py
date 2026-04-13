"""Tests for envchain.env_reorder."""
import pytest
from envchain.env_reorder import EnvReorder, ReorderResult


@pytest.fixture
def reorder():
    return EnvReorder()


@pytest.fixture
def sample_vars():
    return {"C": "3", "A": "1", "B": "2"}


class TestReorderResult:
    def test_is_changed_true_when_order_differs(self):
        r = ReorderResult("p", ["A", "B"], ["B", "A"])
        assert r.is_changed is True

    def test_is_changed_false_when_same(self):
        r = ReorderResult("p", ["A", "B"], ["A", "B"])
        assert r.is_changed is False

    def test_moved_count_correct(self):
        r = ReorderResult("p", ["A", "B", "C"], ["B", "A", "C"])
        assert r.moved_count == 2

    def test_repr_contains_profile(self):
        r = ReorderResult("myprofile", ["A"], ["A"])
        assert "myprofile" in repr(r)


class TestEnvReorder:
    def test_explicit_order_applied(self, reorder, sample_vars):
        result = reorder.reorder(sample_vars, ["A", "B", "C"])
        assert result.new_order == ["A", "B", "C"]

    def test_remainder_appended(self, reorder, sample_vars):
        result = reorder.reorder(sample_vars, ["A"])
        assert result.new_order[0] == "A"
        assert set(result.new_order) == {"A", "B", "C"}

    def test_unknown_keys_recorded(self, reorder, sample_vars):
        result = reorder.reorder(sample_vars, ["A", "Z"])
        assert "Z" in result.unknown_keys

    def test_no_unknown_keys_when_all_present(self, reorder, sample_vars):
        result = reorder.reorder(sample_vars, ["A", "B", "C"])
        assert result.unknown_keys == []

    def test_apply_returns_dict_in_new_order(self, reorder, sample_vars):
        reordered = reorder.apply(sample_vars, ["A", "B", "C"])
        assert list(reordered.keys()) == ["A", "B", "C"]

    def test_apply_preserves_values(self, reorder, sample_vars):
        reordered = reorder.apply(sample_vars, ["B", "A", "C"])
        assert reordered["A"] == "1"
        assert reordered["B"] == "2"
        assert reordered["C"] == "3"

    def test_empty_key_order_leaves_original_order(self, reorder, sample_vars):
        result = reorder.reorder(sample_vars, [])
        assert result.new_order == list(sample_vars.keys())
        assert result.is_changed is False

    def test_profile_name_stored_in_result(self, reorder, sample_vars):
        result = reorder.reorder(sample_vars, ["A"], profile="dev")
        assert result.profile == "dev"
