"""Tests for envchain.env_batch."""
import pytest
from envchain.env_batch import BatchOperation, BatchResult, EnvBatch


@pytest.fixture
def batch():
    return EnvBatch()


@pytest.fixture
def sample_vars():
    return {"EXISTING": "old", "KEEP": "yes"}


class TestBatchOperation:
    def test_repr_set(self):
        op = BatchOperation(action='set', name='FOO', value='bar')
        assert 'set' in repr(op)
        assert 'FOO' in repr(op)

    def test_repr_delete(self):
        op = BatchOperation(action='delete', name='FOO')
        assert 'delete' in repr(op)
        assert 'FOO' in repr(op)


class TestBatchResult:
    def test_applied_count(self):
        r = BatchResult(profile='dev')
        r.applied.append(BatchOperation('set', 'A', '1'))
        assert r.applied_count == 1

    def test_skipped_count(self):
        r = BatchResult(profile='dev')
        r.skipped.append(BatchOperation('delete', 'X'))
        assert r.skipped_count == 1

    def test_has_errors_false_when_empty(self):
        assert not BatchResult(profile='dev').has_errors

    def test_has_errors_true_when_present(self):
        r = BatchResult(profile='dev', errors=['oops'])
        assert r.has_errors

    def test_repr_contains_profile(self):
        r = BatchResult(profile='staging')
        assert 'staging' in repr(r)


class TestEnvBatch:
    def test_set_new_variable(self, batch, sample_vars):
        ops = [BatchOperation('set', 'NEW_VAR', 'hello')]
        result = batch.run('dev', sample_vars, ops)
        assert result.applied_count == 1
        assert result.skipped_count == 0

    def test_set_overwrites_when_allowed(self, batch, sample_vars):
        ops = [BatchOperation('set', 'EXISTING', 'new_val')]
        result = batch.run('dev', sample_vars, ops, allow_overwrite=True)
        assert result.applied_count == 1

    def test_set_skips_when_overwrite_forbidden(self, batch, sample_vars):
        ops = [BatchOperation('set', 'EXISTING', 'new_val')]
        result = batch.run('dev', sample_vars, ops, allow_overwrite=False)
        assert result.skipped_count == 1
        assert result.applied_count == 0

    def test_delete_existing_variable(self, batch, sample_vars):
        ops = [BatchOperation('delete', 'EXISTING')]
        result = batch.run('dev', sample_vars, ops)
        assert result.applied_count == 1

    def test_delete_missing_variable_skipped(self, batch, sample_vars):
        ops = [BatchOperation('delete', 'GHOST')]
        result = batch.run('dev', sample_vars, ops)
        assert result.skipped_count == 1

    def test_unknown_action_adds_error(self, batch, sample_vars):
        ops = [BatchOperation('explode', 'X')]
        result = batch.run('dev', sample_vars, ops)
        assert result.has_errors

    def test_multiple_operations(self, batch, sample_vars):
        ops = [
            BatchOperation('set', 'A', '1'),
            BatchOperation('set', 'B', '2'),
            BatchOperation('delete', 'KEEP'),
        ]
        result = batch.run('dev', sample_vars, ops)
        assert result.applied_count == 3
        assert result.skipped_count == 0
