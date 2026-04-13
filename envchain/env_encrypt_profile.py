"""Per-profile re-encryption support with algorithm selection."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envchain.crypto import EnvCrypto


@dataclass
class ReEncryptResult:
    profile_name: str
    success: bool
    vars_processed: int = 0
    error: Optional[str] = None

    def __repr__(self) -> str:
        status = "ok" if self.success else f"error={self.error}"
        return f"<ReEncryptResult profile={self.profile_name!r} vars={self.vars_processed} {status}>"


@dataclass
class ReEncryptReport:
    results: List[ReEncryptResult] = field(default_factory=list)

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.results if r.success)

    @property
    def failure_count(self) -> int:
        return sum(1 for r in self.results if not r.success)

    @property
    def has_failures(self) -> bool:
        return self.failure_count > 0

    def __repr__(self) -> str:
        return (
            f"<ReEncryptReport total={len(self.results)} "
            f"ok={self.success_count} failed={self.failure_count}>"
        )


class ProfileReEncryptor:
    """Re-encrypts profile variable sets from one password to another."""

    def __init__(self, storage) -> None:
        self._storage = storage

    def re_encrypt(
        self,
        profile_name: str,
        old_password: str,
        new_password: str,
    ) -> ReEncryptResult:
        try:
            profile = self._storage.load_profile(profile_name, old_password)
            if profile is None:
                return ReEncryptResult(
                    profile_name=profile_name,
                    success=False,
                    error="profile not found",
                )
            vars_count = len(profile.vars)
            self._storage.save_profile(profile, new_password)
            return ReEncryptResult(
                profile_name=profile_name,
                success=True,
                vars_processed=vars_count,
            )
        except Exception as exc:  # noqa: BLE001
            return ReEncryptResult(
                profile_name=profile_name,
                success=False,
                error=str(exc),
            )

    def re_encrypt_all(
        self,
        profile_names: List[str],
        old_password: str,
        new_password: str,
    ) -> ReEncryptReport:
        report = ReEncryptReport()
        for name in profile_names:
            result = self.re_encrypt(name, old_password, new_password)
            report.results.append(result)
        return report
