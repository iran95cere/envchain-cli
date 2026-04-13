"""Tests for per-field encryption (env_encrypt_field)."""

import pytest

from envchain.env_encrypt_field import (
    FieldEncryptReport,
    FieldEncryptResult,
    FieldEncryptor,
)


PASSWORD = "test-secret-pw"


@pytest.fixture
def encryptor():
    return FieldEncryptor(PASSWORD)


@pytest.fixture
def sample_vars():
    return {"DB_PASS": "hunter2", "API_KEY": "abc123", "HOST": "localhost"}


# --- FieldEncryptResult ---

class TestFieldEncryptResult:
    def test_repr_encrypted(self):
        r = FieldEncryptResult(name="DB_PASS", encrypted=True, ciphertext="xyz")
        assert "encrypted" in repr(r)
        assert "DB_PASS" in repr(r)

    def test_repr_failed(self):
        r = FieldEncryptResult(name="MISSING", encrypted=False, error="not found")
        assert "failed" in repr(r)
        assert "not found" in repr(r)


# --- FieldEncryptReport ---

class TestFieldEncryptReport:
    def test_encrypted_count(self):
        report = FieldEncryptReport(
            results=[
                FieldEncryptResult("A", encrypted=True),
                FieldEncryptResult("B", encrypted=False, error="x"),
            ]
        )
        assert report.encrypted_count == 1

    def test_failed_count(self):
        report = FieldEncryptReport(
            results=[
                FieldEncryptResult("A", encrypted=True),
                FieldEncryptResult("B", encrypted=False, error="x"),
            ]
        )
        assert report.failed_count == 1

    def test_has_failures_false_when_all_ok(self):
        report = FieldEncryptReport(
            results=[FieldEncryptResult("A", encrypted=True)]
        )
        assert not report.has_failures

    def test_has_failures_true_when_any_fail(self):
        report = FieldEncryptReport(
            results=[FieldEncryptResult("A", encrypted=False, error="e")]
        )
        assert report.has_failures

    def test_repr_contains_counts(self):
        report = FieldEncryptReport()
        assert "encrypted=0" in repr(report)
        assert "failed=0" in repr(report)


# --- FieldEncryptor ---

class TestFieldEncryptor:
    def test_encrypt_and_decrypt_roundtrip(self, encryptor, sample_vars):
        vars_copy = dict(sample_vars)
        encryptor.encrypt_fields(vars_copy, ["DB_PASS", "API_KEY"])
        decrypted = encryptor.decrypt_fields(vars_copy, ["DB_PASS", "API_KEY"])
        assert decrypted["DB_PASS"] == "hunter2"
        assert decrypted["API_KEY"] == "abc123"
        assert decrypted["HOST"] == "localhost"

    def test_encrypt_marks_prefix(self, encryptor, sample_vars):
        vars_copy = dict(sample_vars)
        encryptor.encrypt_fields(vars_copy, ["DB_PASS"])
        assert vars_copy["DB_PASS"].startswith(FieldEncryptor.FIELD_PREFIX)

    def test_encrypt_missing_field_reports_error(self, encryptor):
        vars_copy = {"A": "1"}
        report = encryptor.encrypt_fields(vars_copy, ["MISSING"])
        assert report.results[0].encrypted is False
        assert report.results[0].error == "not found"

    def test_encrypt_already_encrypted_reports_error(self, encryptor, sample_vars):
        vars_copy = dict(sample_vars)
        encryptor.encrypt_fields(vars_copy, ["DB_PASS"])
        report = encryptor.encrypt_fields(vars_copy, ["DB_PASS"])
        assert report.results[0].error == "already encrypted"

    def test_is_field_encrypted_true(self, encryptor, sample_vars):
        vars_copy = dict(sample_vars)
        encryptor.encrypt_fields(vars_copy, ["API_KEY"])
        assert encryptor.is_field_encrypted(vars_copy["API_KEY"])

    def test_is_field_encrypted_false_for_plain(self, encryptor):
        assert not encryptor.is_field_encrypted("plaintext")

    def test_encrypted_fields_returns_names(self, encryptor, sample_vars):
        vars_copy = dict(sample_vars)
        encryptor.encrypt_fields(vars_copy, ["DB_PASS", "API_KEY"])
        names = encryptor.encrypted_fields(vars_copy)
        assert set(names) == {"DB_PASS", "API_KEY"}

    def test_unencrypted_field_not_in_encrypted_list(self, encryptor, sample_vars):
        vars_copy = dict(sample_vars)
        encryptor.encrypt_fields(vars_copy, ["DB_PASS"])
        names = encryptor.encrypted_fields(vars_copy)
        assert "HOST" not in names

    def test_wrong_password_raises_on_decrypt(self, sample_vars):
        enc = FieldEncryptor(PASSWORD)
        vars_copy = dict(sample_vars)
        enc.encrypt_fields(vars_copy, ["DB_PASS"])
        wrong = FieldEncryptor("wrong-password")
        with pytest.raises(Exception):
            wrong.decrypt_fields(vars_copy, ["DB_PASS"])
