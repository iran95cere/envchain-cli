"""Integration tests for profile re-encryption using real storage."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from envchain.env_encrypt_profile import ProfileReEncryptor
from envchain.models import Profile
from envchain.storage import EnvStorage


@pytest.fixture()
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture()
def storage(tmp_dir):
    return EnvStorage(str(tmp_dir))


@pytest.fixture()
def encryptor(storage):
    return ProfileReEncryptor(storage)


def _save_profile(storage, name: str, vars_: dict, password: str) -> Profile:
    p = Profile(name=name)
    for k, v in vars_.items():
        p.add_var(k, v)
    storage.save_profile(p, password)
    return p


class TestProfileReEncryptorIntegration:
    def test_re_encrypt_and_load_with_new_password(self, storage, encryptor):
        _save_profile(storage, "dev", {"KEY": "hello", "SECRET": "world"}, "old_pw")
        result = encryptor.re_encrypt("dev", "old_pw", "new_pw")
        assert result.success
        assert result.vars_processed == 2

        profile = storage.load_profile("dev", "new_pw")
        assert profile is not None
        assert profile.get_var("KEY") == "hello"
        assert profile.get_var("SECRET") == "world"

    def test_old_password_fails_after_re_encrypt(self, storage, encryptor):
        _save_profile(storage, "staging", {"A": "1"}, "original")
        encryptor.re_encrypt("staging", "original", "rotated")

        with pytest.raises(Exception):
            storage.load_profile("staging", "original")

    def test_re_encrypt_all_multiple_profiles(self, storage, encryptor):
        _save_profile(storage, "dev", {"X": "1"}, "pass")
        _save_profile(storage, "prod", {"Y": "2"}, "pass")

        report = encryptor.re_encrypt_all(["dev", "prod"], "pass", "newpass")
        assert report.success_count == 2
        assert not report.has_failures

        dev = storage.load_profile("dev", "newpass")
        prod = storage.load_profile("prod", "newpass")
        assert dev.get_var("X") == "1"
        assert prod.get_var("Y") == "2"

    def test_re_encrypt_wrong_old_password_fails(self, storage, encryptor):
        _save_profile(storage, "dev", {"K": "v"}, "correct")
        result = encryptor.re_encrypt("dev", "wrong", "new")
        assert not result.success
