"""Profile signature/integrity verification for envchain."""
from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional


@dataclass
class SignatureEntry:
    profile_name: str
    signature: str
    algorithm: str
    signed_at: str

    def to_dict(self) -> Dict:
        return {
            "profile_name": self.profile_name,
            "signature": self.signature,
            "algorithm": self.algorithm,
            "signed_at": self.signed_at,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "SignatureEntry":
        return cls(
            profile_name=data["profile_name"],
            signature=data["signature"],
            algorithm=data["algorithm"],
            signed_at=data["signed_at"],
        )

    def __repr__(self) -> str:
        return f"<SignatureEntry profile={self.profile_name!r} algo={self.algorithm!r}>"


@dataclass
class VerifyResult:
    profile_name: str
    valid: bool
    reason: str = ""

    def __bool__(self) -> bool:
        return self.valid

    def __repr__(self) -> str:
        status = "valid" if self.valid else "invalid"
        return f"<VerifyResult profile={self.profile_name!r} status={status!r}>"


class SignatureManager:
    ALGORITHM = "sha256"

    def __init__(self, secret_key: str) -> None:
        if not secret_key:
            raise ValueError("secret_key must not be empty")
        self._key = secret_key.encode()
        self._entries: Dict[str, SignatureEntry] = {}

    def _compute(self, vars_dict: Dict[str, str]) -> str:
        payload = json.dumps(vars_dict, sort_keys=True, separators=(",", ":"))
        return hmac.new(self._key, payload.encode(), hashlib.sha256).hexdigest()

    def sign(self, profile_name: str, vars_dict: Dict[str, str]) -> SignatureEntry:
        sig = self._compute(vars_dict)
        entry = SignatureEntry(
            profile_name=profile_name,
            signature=sig,
            algorithm=self.ALGORITHM,
            signed_at=datetime.now(timezone.utc).isoformat(),
        )
        self._entries[profile_name] = entry
        return entry

    def verify(self, profile_name: str, vars_dict: Dict[str, str]) -> VerifyResult:
        entry = self._entries.get(profile_name)
        if entry is None:
            return VerifyResult(profile_name, False, "no signature found")
        expected = self._compute(vars_dict)
        if hmac.compare_digest(expected, entry.signature):
            return VerifyResult(profile_name, True)
        return VerifyResult(profile_name, False, "signature mismatch")

    def remove(self, profile_name: str) -> bool:
        return self._entries.pop(profile_name, None) is not None

    def list_signed(self):
        return list(self._entries.keys())
