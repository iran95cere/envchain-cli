"""Tests for envchain.env_sort."""
import pytest

from envchain.env_sort import EnvSorter, SortKey, SortOrder, SortResult


@pytest.fixture
def sorter() -> EnvSorter:
    return EnvSorter()


@pytest.fixture
def sample_vars() -> dict:
    return {
        "ZEBRA": "last",
        "ALPHA": "first",
        "MIDDLE": "middle_value",
        "BETA": "bb",
    }


class TestSortResult:
    def test_is_changed_true_when_order_differs(self, sorter, sample_vars):
        result = sorter.sort_by_name(sample_vars)
        assert result.is_changed is True

    def test_is_changed_false_when_already_sorted(self, sorter):
        already = {"ALPHA": "a", "BETA": "b", "GAMMA": "g"}
        result = sorter.sort_by_name(already)
        assert result.is_changed is False

    def test_var_count_matches_input(self, sorter, sample_vars):
        result = sorter.sort_by_name(sample_vars)
        assert result.var_count == len(sample_vars)

    def test_original_preserved(self, sorter, sample_vars):
        result = sorter.sort_by_name(sample_vars)
        assert list(result.original.keys()) == list(sample_vars.keys())


class TestEnvSorterByName:
    def test_sort_ascending_order(self, sorter, sample_vars):
        result = sorter.sort_by_name(sample_vars)
        keys = list(result.sorted_vars.keys())
        assert keys == sorted(keys, key=str.lower)

    def test_sort_descending_order(self, sorter, sample_vars):
        result = sorter.sort_by_name(sample_vars, descending=True)
        keys = list(result.sorted_vars.keys())
        assert keys == sorted(keys, key=str.lower, reverse=True)

    def test_sort_key_is_name(self, sorter, sample_vars):
        result = sorter.sort_by_name(sample_vars)
        assert result.key == SortKey.NAME

    def test_sort_order_asc_by_default(self, sorter, sample_vars):
        result = sorter.sort_by_name(sample_vars)
        assert result.order == SortOrder.ASC


class TestEnvSorterByValue:
    def test_sort_by_value_ascending(self, sorter, sample_vars):
        result = sorter.sort(sample_vars, key=SortKey.VALUE, order=SortOrder.ASC)
        values = list(result.sorted_vars.values())
        assert values == sorted(values, key=str.lower)

    def test_sort_by_value_key_set(self, sorter, sample_vars):
        result = sorter.sort(sample_vars, key=SortKey.VALUE)
        assert result.key == SortKey.VALUE


class TestEnvSorterByLength:
    def test_sort_by_length_ascending(self, sorter, sample_vars):
        result = sorter.sort_by_value_length(sample_vars)
        lengths = [len(v) for v in result.sorted_vars.values()]
        assert lengths == sorted(lengths)

    def test_sort_by_length_key_set(self, sorter, sample_vars):
        result = sorter.sort_by_value_length(sample_vars)
        assert result.key == SortKey.LENGTH


class TestEdgeCases:
    def test_empty_vars_returns_empty_result(self, sorter):
        result = sorter.sort_by_name({})
        assert result.sorted_vars == {}
        assert result.var_count == 0
        assert result.is_changed is False

    def test_single_var_not_changed(self, sorter):
        result = sorter.sort_by_name({"ONLY": "value"})
        assert result.is_changed is False

    def test_case_insensitive_name_sort(self, sorter):
        vars = {"zebra": "z", "ALPHA": "a", "Beta": "b"}
        result = sorter.sort_by_name(vars)
        keys = list(result.sorted_vars.keys())
        assert keys == sorted(keys, key=str.lower)
