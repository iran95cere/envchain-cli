"""Profile PIN lock: require a short numeric PIN before decrypting a profile."""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Optional

_PIN_FILE = ".pin_locks.json"
_MAX_ATTEMPTS = 5
_LOCKOUT_SECONDS = 60


class PinError(Exception):
    """Raised on PIN validation failures."""


class PinManager:
    """Manage per-profile PIN locks stored alongside the profile data."""

    def __init__(self, storage_dir: str) -> None:
        self._dir = Path(storage_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._path = self._dir / _PIN_FILE
        self._data: dict = self._load()

    # ------------------------------------------------------------------
    # persistence
    # ------------------------------------------------------------------

    def _load(self) -> dict:
        if self._path.exists():
            with open(self._path) as fh:
                return json.load(fh)
        return {}

    def _save(self) -> None:
        with open(self._path, "w") as fh:
            json.dump(self._data, fh, indent=2)

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _hash_pin(pin: str) -> str:
        return hashlib.sha256(pin.encode()).hexdigest()

    def _record(self, profile: str) -> dict:
        return self._data.setdefault(profile, {})

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def set_pin(self, profile: str, pin: str) -> None:
        """Set (or replace) the PIN for *profile*."""
        if not pin.isdigit() or len(pin) < 4:
            raise PinError("PIN must be at least 4 digits.")
        rec = self._record(profile)
        rec["hash"] = self._hash_pin(pin)
        rec["attempts"] = 0
        rec["locked_until"] = 0.0
        self._save()

    def remove_pin(self, profile: str) -> bool:
        """Remove the PIN for *profile*. Returns True if one existed."""
        existed = profile in self._data
        self._data.pop(profile, None)
        self._save()
        return existed

    def has_pin(self, profile: str) -> bool:
        return "hash" in self._data.get(profile, {})

    def verify_pin(self, profile: str, pin: str) -> None:
        """Verify *pin* for *profile*. Raises PinError on failure or lockout."""
        if not self.has_pin(profile):
            return  # no PIN set — allow through

        rec = self._record(profile)
        now = time.time()

        if now < rec.get("locked_until", 0.0):
            remaining = int(rec["locked_until"] - now)
            raise PinError(f"Profile locked. Try again in {remaining}s.")

        if self._hash_pin(pin) == rec["hash"]:
            rec["attempts"] = 0
            self._save()
            return

        rec["attempts"] = rec.get("attempts", 0) + 1
        if rec["attempts"] >= _MAX_ATTEMPTS:
            rec["locked_until"] = now + _LOCKOUT_SECONDS
            rec["attempts"] = 0
            self._save()
            raise PinError("Too many failed attempts. Profile locked for 60 seconds.")

        self._save()
        remaining_attempts = _MAX_ATTEMPTS - rec["attempts"]
        raise PinError(f"Incorrect PIN. {remaining_attempts} attempt(s) remaining.")
