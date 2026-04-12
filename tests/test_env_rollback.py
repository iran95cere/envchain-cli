"""Tests for envchain.env_rollback."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from envchain.env_rollback import RollbackRecord, RollbackManager
from envchain.snapshot import Snapshot


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_snapshot(label: str, profile: str, variables: dict) -> Snapshot:
    s = Snapshot(profile=profile, label=label, variables=variables)
    return s


def _make_profile(variables: dict):
    p = MagicMock()
    p.variables = variables
    return p


# ---------------------------------------------------------------------------
# RollbackRecord
# ---------------------------------------------------------------------------

class TestRollbackRecord:
    def test_to_dict_contains_required_keys(self):
        r = RollbackRecord(profile="dev", rolled_back_to="snap-1")
        d = r.to_dict()
        assert "profile" in d
        assert "rolled_back_to" in d
        assert "timestamp" in d
        assert "previous_vars" in d

    def test_from_dict_roundtrip(self):
        r = RollbackRecord(
            profile="prod",
            rolled_back_to="snap-2",
            previous_vars={"A": "1"},
        )
        r2 = RollbackRecord.from_dict(r.to_dict())
        assert r2.profile == r.profile
        assert r2.rolled_back_to == r.rolled_back_to
        assert r2.previous_vars == r.previous_vars

    def test_repr_contains_profile_and_label(self):
        r = RollbackRecord(profile="staging", rolled_back_to="v1")
        assert "staging" in repr(r)
        assert "v1" in repr(r)


# ---------------------------------------------------------------------------
# RollbackManager
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_storage():
    storage = MagicMock()
    profile = _make_profile({"KEY": "old"})
    storage.load_profile.return_value = profile
    return storage


@pytest.fixture()
def mock_snapshot_manager():
    sm = MagicMock()
    sm.list_snapshots.return_value = [
        _make_snapshot("snap-1", "dev", {"KEY": "new"}),
        _make_snapshot("snap-2", "dev", {"KEY": "older"}),
    ]
    return sm


def test_list_snapshots_filters_by_profile(mock_storage, mock_snapshot_manager):
    mgr = RollbackManager(mock_storage, mock_snapshot_manager)
    snaps = mgr.list_snapshots("dev")
    assert all(s.profile == "dev" for s in snaps)
    assert len(snaps) == 2


def test_rollback_applies_snapshot_vars(mock_storage, mock_snapshot_manager):
    mgr = RollbackManager(mock_storage, mock_snapshot_manager)
    record = mgr.rollback("dev", "snap-1", "secret")
    saved_profile = mock_storage.save_profile.call_args[0][0]
    assert saved_profile.variables == {"KEY": "new"}
    assert record.previous_vars == {"KEY": "old"}


def test_rollback_unknown_snapshot_raises(mock_storage, mock_snapshot_manager):
    mgr = RollbackManager(mock_storage, mock_snapshot_manager)
    with pytest.raises(KeyError, match="snap-99"):
        mgr.rollback("dev", "snap-99", "secret")


def test_rollback_record_profile_matches(mock_storage, mock_snapshot_manager):
    mgr = RollbackManager(mock_storage, mock_snapshot_manager)
    record = mgr.rollback("dev", "snap-2", "pw")
    assert record.profile == "dev"
    assert record.rolled_back_to == "snap-2"
