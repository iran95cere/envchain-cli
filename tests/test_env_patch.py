"""Tests for envchain.env_patch."""
import pytest
from envchain.env_patch import EnvPatcher, PatchOperation, PatchResult


@pytest.fixture
def patcher():
    return EnvPatcher()


@pytest.fixture
def sample_vars():
    return {'FOO': 'foo', 'BAR': 'bar'}


class TestPatchOperation:
    def test_repr_set(self):
        op = PatchOperation(op='set', key='X', value='1')
        assert 'set' in repr(op)
        assert 'X' in repr(op)

    def test_repr_delete(self):
        op = PatchOperation(op='delete', key='X')
        assert 'delete' in repr(op)
        assert 'X' in repr(op)


class TestPatchResult:
    def test_applied_count(self):
        r = PatchResult()
        r.applied.append(PatchOperation('set', 'A', '1'))
        assert r.applied_count == 1

    def test_skipped_count(self):
        r = PatchResult()
        r.skipped.append((PatchOperation('delete', 'Z'), 'not found'))
        assert r.skipped_count == 1

    def test_has_skipped_false_when_empty(self):
        assert not PatchResult().has_skipped

    def test_has_skipped_true_when_present(self):
        r = PatchResult()
        r.skipped.append((PatchOperation('delete', 'Z'), 'reason'))
        assert r.has_skipped

    def test_repr_contains_counts(self):
        r = PatchResult()
        assert 'applied=0' in repr(r)
        assert 'skipped=0' in repr(r)


class TestEnvPatcher:
    def test_set_adds_new_key(self, patcher, sample_vars):
        ops = [PatchOperation('set', 'NEW', 'value')]
        result = patcher.apply(sample_vars, ops)
        assert sample_vars['NEW'] == 'value'
        assert result.applied_count == 1

    def test_set_overwrites_existing_key(self, patcher, sample_vars):
        ops = [PatchOperation('set', 'FOO', 'updated')]
        patcher.apply(sample_vars, ops)
        assert sample_vars['FOO'] == 'updated'

    def test_delete_removes_key(self, patcher, sample_vars):
        ops = [PatchOperation('delete', 'FOO')]
        result = patcher.apply(sample_vars, ops)
        assert 'FOO' not in sample_vars
        assert result.applied_count == 1

    def test_delete_missing_key_skipped_by_default(self, patcher, sample_vars):
        ops = [PatchOperation('delete', 'MISSING')]
        result = patcher.apply(sample_vars, ops)
        assert result.skipped_count == 1
        assert result.applied_count == 0

    def test_delete_missing_key_allowed(self, patcher, sample_vars):
        ops = [PatchOperation('delete', 'MISSING')]
        result = patcher.apply(sample_vars, ops, allow_delete_missing=True)
        assert result.applied_count == 1
        assert result.skipped_count == 0

    def test_empty_key_skipped(self, patcher, sample_vars):
        ops = [PatchOperation('set', '', 'value')]
        result = patcher.apply(sample_vars, ops)
        assert result.skipped_count == 1

    def test_unknown_op_skipped(self, patcher, sample_vars):
        ops = [PatchOperation('rename', 'FOO', 'BAZ')]
        result = patcher.apply(sample_vars, ops)
        assert result.skipped_count == 1

    def test_multiple_ops_applied_in_order(self, patcher):
        v = {'A': '1'}
        ops = [
            PatchOperation('set', 'B', '2'),
            PatchOperation('delete', 'A'),
        ]
        result = patcher.apply(v, ops)
        assert 'A' not in v
        assert v['B'] == '2'
        assert result.applied_count == 2
