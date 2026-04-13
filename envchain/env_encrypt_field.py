"""Per-field encryption support for environment variable profiles."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envchain.crypto import EnvCrypto


@dataclass
class FieldEncryptResult:
    name: str
    encrypted: bool
    ciphertext: Optional[str] = None
    error: Optional[str] = None

    def __repr__(self) -> str:
        status = "encrypted" if self.encrypted else f"failed({self.error})"
        return f"<FieldEncryptResult name={self.name!r} status={status}>"


@dataclass
class FieldEncryptReport:
    results: List[FieldEncryptResult] = field(default_factory=list)

    @property
    def encrypted_count(self) -> int:
        return sum(1 for r in self.results if r.encrypted)

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if not r.encrypted)

    @property
    def has_failures(self) -> bool:
        return self.failed_count > 0

    def __repr__(self) -> str:
        return (
            f"<FieldEncryptReport encrypted={self.encrypted_count} "
            f"failed={self.failed_count}>"
        )


class FieldEncryptor:
    """Encrypt or decrypt individual fields within a vars dict."""

    FIELD_PREFIX = "enc:"

    def __init__(self, password: str) -> None:
        self._crypto = EnvCrypto(password)

    def encrypt_fields(
        self, vars_dict: Dict[str, str], field_names: List[str]
    ) -> FieldEncryptReport:
        """Encrypt the specified fields in vars_dict in-place and return a report."""
        report = FieldEncryptReport()
        for name in field_names:
            if name not in vars_dict:
                report.results.append(
                    FieldEncryptResult(name=name, encrypted=False, error="not found")
                )
                continue
            value = vars_dict[name]
            if value.startswith(self.FIELD_PREFIX):
                report.results.append(
                    FieldEncryptResult(name=name, encrypted=False, error="already encrypted")
                )
                continue
            try:
                ciphertext = self._crypto.encrypt(value)
                vars_dict[name] = self.FIELD_PREFIX + ciphertext
                report.results.append(
                    FieldEncryptResult(name=name, encrypted=True, ciphertext=ciphertext)
                )
            except Exception as exc:  # pragma: no cover
                report.results.append(
                    FieldEncryptResult(name=name, encrypted=False, error=str(exc))
                )
        return report

    def decrypt_fields(
        self, vars_dict: Dict[str, str], field_names: List[str]
    ) -> Dict[str, str]:
        """Return a copy of vars_dict with specified encrypted fields decrypted."""
        result = dict(vars_dict)
        for name in field_names:
            value = result.get(name, "")
            if value.startswith(self.FIELD_PREFIX):
                ciphertext = value[len(self.FIELD_PREFIX):]
                result[name] = self._crypto.decrypt(ciphertext)
        return result

    def is_field_encrypted(self, value: str) -> bool:
        return value.startswith(self.FIELD_PREFIX)

    def encrypted_fields(self, vars_dict: Dict[str, str]) -> List[str]:
        """Return names of all fields that are currently encrypted."""
        return [k for k, v in vars_dict.items() if self.is_field_encrypted(v)]
