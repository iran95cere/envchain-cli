"""Tests for encryption and decryption utilities."""

import pytest
from envchain.crypto import EnvCrypto


class TestEnvCrypto:
    """Test cases for EnvCrypto class."""

    def test_encrypt_decrypt_roundtrip(self):
        """Test that encryption and decryption work correctly."""
        password = "test_password_123"
        plaintext = "SECRET_KEY=my_secret_value"
        
        crypto = EnvCrypto(password)
        encrypted = crypto.encrypt(plaintext)
        decrypted = crypto.decrypt(encrypted)
        
        assert decrypted == plaintext
        assert encrypted != plaintext.encode()

    def test_different_passwords_produce_different_ciphertext(self):
        """Test that different passwords produce different encrypted results."""
        plaintext = "API_KEY=12345"
        
        crypto1 = EnvCrypto("password1")
        crypto2 = EnvCrypto("password2")
        
        encrypted1 = crypto1.encrypt(plaintext)
        encrypted2 = crypto2.encrypt(plaintext)
        
        assert encrypted1 != encrypted2

    def test_same_password_with_same_salt_decrypts(self):
        """Test that same password and salt can decrypt data."""
        password = "shared_password"
        plaintext = "DB_URL=postgresql://localhost/db"
        
        crypto1 = EnvCrypto(password)
        salt = crypto1.get_salt()
        encrypted = crypto1.encrypt(plaintext)
        
        # Create new crypto instance with same password and salt
        crypto2 = EnvCrypto(password, salt=salt)
        decrypted = crypto2.decrypt(encrypted)
        
        assert decrypted == plaintext

    def test_wrong_password_fails_decryption(self):
        """Test that wrong password cannot decrypt data."""
        plaintext = "TOKEN=abc123"
        
        crypto1 = EnvCrypto("correct_password")
        salt = crypto1.get_salt()
        encrypted = crypto1.encrypt(plaintext)
        
        crypto2 = EnvCrypto("wrong_password", salt=salt)
        
        with pytest.raises(Exception):
            crypto2.decrypt(encrypted)

    def test_encrypt_empty_string(self):
        """Test encryption of empty string."""
        crypto = EnvCrypto("password")
        encrypted = crypto.encrypt("")
        decrypted = crypto.decrypt(encrypted)
        
        assert decrypted == ""

    def test_encrypt_multiline_data(self):
        """Test encryption of multiline environment data."""
        crypto = EnvCrypto("password")
        plaintext = "KEY1=value1\nKEY2=value2\nKEY3=value3"
        
        encrypted = crypto.encrypt(plaintext)
        decrypted = crypto.decrypt(encrypted)
        
        assert decrypted == plaintext

    def test_salt_is_generated_when_not_provided(self):
        """Test that salt is automatically generated."""
        crypto = EnvCrypto("password")
        salt = crypto.get_salt()
        
        assert salt is not None
        assert len(salt) == 16
