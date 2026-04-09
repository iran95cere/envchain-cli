"""Encryption and decryption utilities for environment variables."""

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend


class EnvCrypto:
    """Handle encryption and decryption of environment variables."""

    def __init__(self, password: str, salt: bytes = None):
        """
        Initialize crypto handler with password.

        Args:
            password: Master password for encryption/decryption
            salt: Optional salt for key derivation (generated if not provided)
        """
        self.salt = salt if salt is not None else os.urandom(16)
        self.key = self._derive_key(password, self.salt)
        self.cipher = Fernet(self.key)

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Derive encryption key from password using PBKDF2.

        Args:
            password: Master password
            salt: Salt for key derivation

        Returns:
            Base64-encoded key suitable for Fernet
        """
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def encrypt(self, data: str) -> bytes:
        """
        Encrypt plaintext data.

        Args:
            data: Plaintext string to encrypt

        Returns:
            Encrypted bytes
        """
        return self.cipher.encrypt(data.encode())

    def decrypt(self, encrypted_data: bytes) -> str:
        """
        Decrypt encrypted data.

        Args:
            encrypted_data: Encrypted bytes

        Returns:
            Decrypted plaintext string
        """
        return self.cipher.decrypt(encrypted_data).decode()

    def get_salt(self) -> bytes:
        """
        Get the salt used for key derivation.

        Returns:
            Salt bytes
        """
        return self.salt
